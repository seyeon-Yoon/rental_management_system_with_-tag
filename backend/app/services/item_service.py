from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_

from app.models.item import Item
from app.models.category import Category
from app.models.rental import Rental
from app.models.reservation import Reservation
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemList, ItemFilter, ItemStatus
from app.models.audit_log import AuditLog


class ItemService:
    """품목 관리 서비스"""
    
    @staticmethod
    def get_items(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[ItemFilter] = None
    ) -> ItemList:
        """
        품목 목록 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            filters: 필터 조건
            
        Returns:
            ItemList: 품목 목록과 통계
        """
        query = db.query(Item).options(
            joinedload(Item.category),
            joinedload(Item.current_rental),
            joinedload(Item.current_reservation)
        )
        
        # 필터 적용
        if filters:
            if filters.category_id:
                query = query.filter(Item.category_id == filters.category_id)
            
            if filters.status:
                query = query.filter(Item.status == filters.status)
            
            if filters.is_active is not None:
                query = query.filter(Item.is_active == filters.is_active)
            
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Item.name.ilike(search_term),
                        Item.description.ilike(search_term),
                        Item.serial_number.ilike(search_term)
                    )
                )
        
        # 총 개수 조회 (필터 적용된 상태)
        total = query.count()
        
        # 페이지네이션 적용하여 품목 조회
        items = query.offset(skip).limit(limit).all()
        
        # 품목 응답 데이터 생성
        item_responses = []
        for item in items:
            item_data = ItemResponse.model_validate(item)
            item_data.category_name = item.category.name if item.category else None
            item_data.current_rental_id = item.current_rental.id if item.current_rental else None
            item_data.current_reservation_id = item.current_reservation.id if item.current_reservation else None
            item_responses.append(item_data)
        
        # 상태별 통계 조회 (전체 품목 기준)
        stats_query = db.query(Item.status, func.count(Item.id)).group_by(Item.status)
        if filters and filters.category_id:
            stats_query = stats_query.filter(Item.category_id == filters.category_id)
        
        status_stats = dict(stats_query.all())
        
        return ItemList(
            items=item_responses,
            total=total,
            available_count=status_stats.get(ItemStatus.AVAILABLE, 0),
            rented_count=status_stats.get(ItemStatus.RENTED, 0),
            reserved_count=status_stats.get(ItemStatus.RESERVED, 0),
            maintenance_count=status_stats.get(ItemStatus.MAINTENANCE, 0)
        )
    
    @staticmethod
    def get_item(db: Session, item_id: int) -> Optional[ItemResponse]:
        """
        특정 품목 조회
        
        Args:
            db: 데이터베이스 세션
            item_id: 품목 ID
            
        Returns:
            ItemResponse: 품목 정보
        """
        item = db.query(Item).options(
            joinedload(Item.category),
            joinedload(Item.current_rental),
            joinedload(Item.current_reservation)
        ).filter(Item.id == item_id).first()
        
        if not item:
            return None
        
        item_data = ItemResponse.model_validate(item)
        item_data.category_name = item.category.name if item.category else None
        item_data.current_rental_id = item.current_rental.id if item.current_rental else None
        item_data.current_reservation_id = item.current_reservation.id if item.current_reservation else None
        
        return item_data
    
    @staticmethod
    def get_item_by_serial(db: Session, serial_number: str) -> Optional[ItemResponse]:
        """
        일련번호로 품목 조회
        
        Args:
            db: 데이터베이스 세션
            serial_number: 일련번호
            
        Returns:
            ItemResponse: 품목 정보
        """
        item = db.query(Item).options(
            joinedload(Item.category),
            joinedload(Item.current_rental),
            joinedload(Item.current_reservation)
        ).filter(Item.serial_number == serial_number).first()
        
        if not item:
            return None
        
        item_data = ItemResponse.model_validate(item)
        item_data.category_name = item.category.name if item.category else None
        item_data.current_rental_id = item.current_rental.id if item.current_rental else None
        item_data.current_reservation_id = item.current_reservation.id if item.current_reservation else None
        
        return item_data
    
    @staticmethod
    def create_item(
        db: Session, 
        item_data: ItemCreate, 
        user_id: int,
        ip_address: str = None
    ) -> ItemResponse:
        """
        새 품목 생성
        
        Args:
            db: 데이터베이스 세션
            item_data: 품목 생성 데이터
            user_id: 생성자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            ItemResponse: 생성된 품목 정보
        """
        # 카테고리 존재 확인
        category = db.query(Category).filter(
            and_(
                Category.id == item_data.category_id,
                Category.is_active == True
            )
        ).first()
        
        if not category:
            raise ValueError(f"존재하지 않거나 비활성화된 카테고리입니다: {item_data.category_id}")
        
        # 일련번호 중복 확인
        existing_item = db.query(Item).filter(
            Item.serial_number == item_data.serial_number
        ).first()
        
        if existing_item:
            raise ValueError(f"이미 존재하는 일련번호입니다: {item_data.serial_number}")
        
        # 새 품목 생성
        item = Item(
            name=item_data.name,
            description=item_data.description,
            serial_number=item_data.serial_number,
            category_id=item_data.category_id,
            item_metadata=item_data.item_metadata,
            status=ItemStatus.AVAILABLE
        )
        
        db.add(item)
        db.commit()
        db.refresh(item)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="ITEM_CREATED",
            table_name="items",
            user_id=user_id,
            record_id=item.id,
            description=f"품목 생성: {item.name} ({item.serial_number})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 응답 데이터 생성
        item_data = ItemResponse.model_validate(item)
        item_data.category_name = category.name
        item_data.current_rental_id = None
        item_data.current_reservation_id = None
        
        return item_data
    
    @staticmethod
    def update_item(
        db: Session, 
        item_id: int, 
        item_data: ItemUpdate,
        user_id: int,
        ip_address: str = None
    ) -> Optional[ItemResponse]:
        """
        품목 정보 수정
        
        Args:
            db: 데이터베이스 세션
            item_id: 품목 ID
            item_data: 수정할 데이터
            user_id: 수정자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            ItemResponse: 수정된 품목 정보
        """
        item = db.query(Item).options(
            joinedload(Item.category)
        ).filter(Item.id == item_id).first()
        
        if not item:
            return None
        
        # 기존 데이터 백업 (감사 로그용)
        old_data = {
            "name": item.name,
            "description": item.description,
            "status": item.status.value,
            "category_id": item.category_id,
            "item_metadata": item.item_metadata,
            "is_active": item.is_active
        }
        
        # 카테고리 변경 시 존재 확인
        if item_data.category_id and item_data.category_id != item.category_id:
            category = db.query(Category).filter(
                and_(
                    Category.id == item_data.category_id,
                    Category.is_active == True
                )
            ).first()
            
            if not category:
                raise ValueError(f"존재하지 않거나 비활성화된 카테고리입니다: {item_data.category_id}")
        
        # 상태 변경 유효성 검증
        if item_data.status and item_data.status != item.status:
            if not ItemService._validate_status_change(db, item, item_data.status):
                raise ValueError(f"현재 상태에서 {item_data.status.value}로 변경할 수 없습니다")
        
        # 데이터 업데이트
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        db.commit()
        db.refresh(item)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="ITEM_UPDATED",
            table_name="items",
            user_id=user_id,
            record_id=item.id,
            description=f"품목 수정: {item.name} ({item.serial_number})",
            old_data=old_data,
            new_data=update_data,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 응답 데이터 생성
        item_response = ItemResponse.model_validate(item)
        item_response.category_name = item.category.name if item.category else None
        item_response.current_rental_id = item.current_rental.id if item.current_rental else None
        item_response.current_reservation_id = item.current_reservation.id if item.current_reservation else None
        
        return item_response
    
    @staticmethod
    def delete_item(
        db: Session, 
        item_id: int,
        user_id: int,
        ip_address: str = None
    ) -> bool:
        """
        품목 삭제 (소프트 삭제)
        
        Args:
            db: 데이터베이스 세션
            item_id: 품목 ID
            user_id: 삭제자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            bool: 삭제 성공 여부
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return False
        
        # 대여중이거나 예약된 품목은 삭제 불가
        if item.status in [ItemStatus.RENTED, ItemStatus.RESERVED]:
            raise ValueError(f"대여중이거나 예약된 품목은 삭제할 수 없습니다 (현재 상태: {item.status.value})")
        
        # 소프트 삭제 실행
        item.is_active = False
        item.status = ItemStatus.MAINTENANCE  # 정비중으로 상태 변경
        db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="ITEM_DELETED",
            table_name="items",
            user_id=user_id,
            record_id=item.id,
            description=f"품목 삭제: {item.name} ({item.serial_number})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return True
    
    @staticmethod
    def get_available_items(
        db: Session, 
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ItemResponse]:
        """
        대여 가능한 품목 조회
        
        Args:
            db: 데이터베이스 세션
            category_id: 카테고리 ID (선택사항)
            skip: 건너뛸 개수
            limit: 조회할 개수
            
        Returns:
            List[ItemResponse]: 대여 가능한 품목 목록
        """
        query = db.query(Item).options(
            joinedload(Item.category)
        ).filter(
            and_(
                Item.status == ItemStatus.AVAILABLE,
                Item.is_active == True
            )
        )
        
        if category_id:
            query = query.filter(Item.category_id == category_id)
        
        items = query.offset(skip).limit(limit).all()
        
        item_responses = []
        for item in items:
            item_data = ItemResponse.model_validate(item)
            item_data.category_name = item.category.name if item.category else None
            item_responses.append(item_data)
        
        return item_responses
    
    @staticmethod
    def _validate_status_change(db: Session, item: Item, new_status: ItemStatus) -> bool:
        """
        상태 변경 유효성 검증
        
        Args:
            db: 데이터베이스 세션
            item: 품목 객체
            new_status: 새로운 상태
            
        Returns:
            bool: 변경 가능 여부
        """
        current_status = item.status
        
        # 상태 변경 규칙 정의
        valid_transitions = {
            ItemStatus.AVAILABLE: [ItemStatus.RESERVED, ItemStatus.MAINTENANCE],
            ItemStatus.RESERVED: [ItemStatus.AVAILABLE, ItemStatus.RENTED, ItemStatus.MAINTENANCE],
            ItemStatus.RENTED: [ItemStatus.AVAILABLE, ItemStatus.MAINTENANCE],
            ItemStatus.MAINTENANCE: [ItemStatus.AVAILABLE]
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    def get_item_statistics(db: Session) -> dict:
        """
        품목 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            dict: 품목 통계 정보
        """
        # 전체 품목 개수
        total_items = db.query(func.count(Item.id)).filter(Item.is_active == True).scalar()
        
        # 상태별 품목 개수
        status_counts = db.query(
            Item.status, 
            func.count(Item.id)
        ).filter(Item.is_active == True).group_by(Item.status).all()
        
        # 카테고리별 품목 개수
        category_counts = db.query(
            Category.name,
            func.count(Item.id)
        ).join(Item).filter(
            and_(Item.is_active == True, Category.is_active == True)
        ).group_by(Category.id, Category.name).all()
        
        return {
            "total_items": total_items,
            "status_counts": {status.value: count for status, count in status_counts},
            "category_counts": [
                {"category": name, "count": count} 
                for name, count in category_counts
            ]
        }