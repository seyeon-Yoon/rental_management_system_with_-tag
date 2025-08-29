from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList
from app.models.audit_log import AuditLog


class CategoryService:
    """카테고리 관리 서비스"""
    
    @staticmethod
    def get_categories(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        include_inactive: bool = False
    ) -> CategoryList:
        """
        카테고리 목록 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            include_inactive: 비활성 카테고리 포함 여부
            
        Returns:
            CategoryList: 카테고리 목록과 통계
        """
        query = db.query(Category)
        
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        
        # 총 개수 조회
        total = query.count()
        
        # 페이지네이션 적용하여 카테고리 조회
        categories = query.offset(skip).limit(limit).all()
        
        # 각 카테고리별 활성 품목 개수 조회
        category_responses = []
        for category in categories:
            active_items_count = db.query(func.count(Item.id)).filter(
                and_(
                    Item.category_id == category.id,
                    Item.is_active == True
                )
            ).scalar()
            
            category_data = CategoryResponse.model_validate(category)
            category_data.active_items_count = active_items_count
            category_responses.append(category_data)
        
        return CategoryList(categories=category_responses, total=total)
    
    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[CategoryResponse]:
        """
        특정 카테고리 조회
        
        Args:
            db: 데이터베이스 세션
            category_id: 카테고리 ID
            
        Returns:
            CategoryResponse: 카테고리 정보
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        # 활성 품목 개수 조회
        active_items_count = db.query(func.count(Item.id)).filter(
            and_(
                Item.category_id == category.id,
                Item.is_active == True
            )
        ).scalar()
        
        category_data = CategoryResponse.model_validate(category)
        category_data.active_items_count = active_items_count
        return category_data
    
    @staticmethod
    def create_category(
        db: Session, 
        category_data: CategoryCreate, 
        user_id: int,
        ip_address: str = None
    ) -> CategoryResponse:
        """
        새 카테고리 생성
        
        Args:
            db: 데이터베이스 세션
            category_data: 카테고리 생성 데이터
            user_id: 생성자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            CategoryResponse: 생성된 카테고리 정보
        """
        # 카테고리명 중복 확인
        existing_category = db.query(Category).filter(
            Category.name == category_data.name
        ).first()
        
        if existing_category:
            raise ValueError(f"이미 존재하는 카테고리명입니다: {category_data.name}")
        
        # 새 카테고리 생성
        category = Category(
            name=category_data.name,
            description=category_data.description
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="CATEGORY_CREATED",
            table_name="categories",
            user_id=user_id,
            record_id=category.id,
            description=f"카테고리 생성: {category.name}",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 활성 품목 개수는 0으로 설정
        category_data = CategoryResponse.model_validate(category)
        category_data.active_items_count = 0
        return category_data
    
    @staticmethod
    def update_category(
        db: Session, 
        category_id: int, 
        category_data: CategoryUpdate,
        user_id: int,
        ip_address: str = None
    ) -> Optional[CategoryResponse]:
        """
        카테고리 정보 수정
        
        Args:
            db: 데이터베이스 세션
            category_id: 카테고리 ID
            category_data: 수정할 데이터
            user_id: 수정자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            CategoryResponse: 수정된 카테고리 정보
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        # 기존 데이터 백업 (감사 로그용)
        old_data = {
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active
        }
        
        # 카테고리명 중복 확인 (자신 제외)
        if category_data.name and category_data.name != category.name:
            existing_category = db.query(Category).filter(
                and_(
                    Category.name == category_data.name,
                    Category.id != category_id
                )
            ).first()
            
            if existing_category:
                raise ValueError(f"이미 존재하는 카테고리명입니다: {category_data.name}")
        
        # 데이터 업데이트
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        db.commit()
        db.refresh(category)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="CATEGORY_UPDATED",
            table_name="categories",
            user_id=user_id,
            record_id=category.id,
            description=f"카테고리 수정: {category.name}",
            old_data=old_data,
            new_data=update_data,
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 활성 품목 개수 조회
        active_items_count = db.query(func.count(Item.id)).filter(
            and_(
                Item.category_id == category.id,
                Item.is_active == True
            )
        ).scalar()
        
        category_response = CategoryResponse.model_validate(category)
        category_response.active_items_count = active_items_count
        return category_response
    
    @staticmethod
    def delete_category(
        db: Session, 
        category_id: int,
        user_id: int,
        ip_address: str = None
    ) -> bool:
        """
        카테고리 삭제 (소프트 삭제)
        
        Args:
            db: 데이터베이스 세션
            category_id: 카테고리 ID
            user_id: 삭제자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            bool: 삭제 성공 여부
        """
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        
        # 카테고리에 속한 활성 품목이 있는지 확인
        active_items_count = db.query(func.count(Item.id)).filter(
            and_(
                Item.category_id == category_id,
                Item.is_active == True
            )
        ).scalar()
        
        if active_items_count > 0:
            raise ValueError(f"카테고리에 {active_items_count}개의 활성 품목이 있어 삭제할 수 없습니다")
        
        # 소프트 삭제 실행
        category.is_active = False
        db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="CATEGORY_DELETED",
            table_name="categories",
            user_id=user_id,
            record_id=category.id,
            description=f"카테고리 삭제: {category.name}",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return True
    
    @staticmethod
    def get_category_statistics(db: Session) -> dict:
        """
        카테고리 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            dict: 카테고리 통계 정보
        """
        # 전체 카테고리 개수
        total_categories = db.query(func.count(Category.id)).scalar()
        
        # 활성 카테고리 개수
        active_categories = db.query(func.count(Category.id)).filter(
            Category.is_active == True
        ).scalar()
        
        # 카테고리별 품목 개수
        category_items = db.query(
            Category.name,
            func.count(Item.id).label('item_count')
        ).outerjoin(
            Item, and_(Item.category_id == Category.id, Item.is_active == True)
        ).filter(
            Category.is_active == True
        ).group_by(Category.id, Category.name).all()
        
        return {
            "total_categories": total_categories,
            "active_categories": active_categories,
            "category_item_counts": [
                {"category": name, "item_count": count} 
                for name, count in category_items
            ]
        }