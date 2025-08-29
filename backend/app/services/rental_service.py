from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_
from datetime import datetime, timedelta

from app.models.rental import Rental
from app.models.item import Item, ItemStatus
from app.models.user import User
from app.models.category import Category
from app.models.reservation import Reservation
from app.schemas.rental import (
    RentalCreate, RentalUpdate, RentalResponse, RentalList, 
    RentalFilter, RentalStatus, RentalReturn, RentalExtend, RentalHistory
)
from app.models.audit_log import AuditLog
from app.core.config import settings


class RentalService:
    """대여 관리 서비스"""
    
    RENTAL_DURATION_DAYS = 7  # 기본 대여 기간 (7일)
    MAX_EXTEND_DAYS = 7       # 최대 연장 가능 일수
    
    @staticmethod
    def get_rentals(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[RentalFilter] = None,
        current_user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> RentalList:
        """
        대여 목록 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            filters: 필터 조건
            current_user_id: 현재 사용자 ID (일반 사용자는 자신 것만)
            is_admin: 관리자 여부
            
        Returns:
            RentalList: 대여 목록과 통계
        """
        query = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item).joinedload(Item.category)
        )
        
        # 일반 사용자는 자신의 대여만 조회 가능
        if not is_admin and current_user_id:
            query = query.filter(Rental.user_id == current_user_id)
        
        # 필터 적용
        if filters:
            if filters.user_id and is_admin:  # 관리자만 다른 사용자 필터 가능
                query = query.filter(Rental.user_id == filters.user_id)
            
            if filters.item_id:
                query = query.filter(Rental.item_id == filters.item_id)
            
            if filters.category_id:
                query = query.join(Item).filter(Item.category_id == filters.category_id)
            
            if filters.status:
                query = query.filter(Rental.status == filters.status)
            
            if filters.is_overdue is not None:
                now = datetime.utcnow()
                if filters.is_overdue:
                    query = query.filter(
                        and_(
                            Rental.due_date < now,
                            Rental.status.in_([RentalStatus.ACTIVE, RentalStatus.OVERDUE])
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            Rental.due_date >= now,
                            Rental.status.in_([RentalStatus.RETURNED, RentalStatus.LOST])
                        )
                    )
            
            if filters.date_from:
                query = query.filter(Rental.created_at >= filters.date_from)
            
            if filters.date_to:
                query = query.filter(Rental.created_at <= filters.date_to)
                
            if filters.due_date_from:
                query = query.filter(Rental.due_date >= filters.due_date_from)
                
            if filters.due_date_to:
                query = query.filter(Rental.due_date <= filters.due_date_to)
        
        # 총 개수 조회
        total = query.count()
        
        # 페이지네이션 적용하여 대여 조회 (최신 순)
        rentals = query.order_by(Rental.created_at.desc()).offset(skip).limit(limit).all()
        
        # 대여 응답 데이터 생성
        rental_responses = []
        for rental in rentals:
            rental_data = RentalService._build_rental_response(rental)
            rental_responses.append(rental_data)
        
        # 상태별 통계 조회
        stats_base_query = db.query(Rental.status, func.count(Rental.id)).group_by(Rental.status)
        if not is_admin and current_user_id:
            stats_base_query = stats_base_query.filter(Rental.user_id == current_user_id)
        
        status_stats = dict(stats_base_query.all())
        
        return RentalList(
            rentals=rental_responses,
            total=total,
            active_count=status_stats.get(RentalStatus.ACTIVE, 0),
            returned_count=status_stats.get(RentalStatus.RETURNED, 0),
            overdue_count=status_stats.get(RentalStatus.OVERDUE, 0),
            lost_count=status_stats.get(RentalStatus.LOST, 0)
        )
    
    @staticmethod
    def get_rental(
        db: Session, 
        rental_id: int,
        current_user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> Optional[RentalResponse]:
        """
        특정 대여 조회
        
        Args:
            db: 데이터베이스 세션
            rental_id: 대여 ID
            current_user_id: 현재 사용자 ID
            is_admin: 관리자 여부
            
        Returns:
            RentalResponse: 대여 정보
        """
        query = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item).joinedload(Item.category)
        ).filter(Rental.id == rental_id)
        
        # 일반 사용자는 자신의 대여만 조회 가능
        if not is_admin and current_user_id:
            query = query.filter(Rental.user_id == current_user_id)
        
        rental = query.first()
        if not rental:
            return None
        
        return RentalService._build_rental_response(rental)
    
    @staticmethod
    def create_rental(
        db: Session,
        rental_data: RentalCreate,
        user_id: int,
        admin_user_id: int,
        ip_address: str = None
    ) -> RentalResponse:
        """
        새 대여 생성 (예약 확인 시 자동 생성)
        
        Args:
            db: 데이터베이스 세션
            rental_data: 대여 생성 데이터
            user_id: 대여자 ID
            admin_user_id: 관리자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            RentalResponse: 생성된 대여 정보
            
        Raises:
            ValueError: 대여 불가능한 경우
        """
        # 품목 존재 및 대여 가능 여부 확인
        item = db.query(Item).options(joinedload(Item.category)).filter(
            and_(
                Item.id == rental_data.item_id,
                Item.is_active == True
            )
        ).first()
        
        if not item:
            raise ValueError("존재하지 않거나 비활성화된 품목입니다")
        
        if item.status != ItemStatus.RENTED:
            raise ValueError(f"현재 대여 상태가 아닌 품목입니다 (상태: {item.status.value})")
        
        # 사용자 존재 확인
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("존재하지 않는 사용자입니다")
        
        # 반납 예정일 계산 (7일 후)
        due_date = datetime.utcnow() + timedelta(days=RentalService.RENTAL_DURATION_DAYS)
        
        # 새 대여 생성
        rental = Rental(
            user_id=user_id,
            item_id=rental_data.item_id,
            reservation_id=rental_data.reservation_id,
            notes=rental_data.notes,
            status=RentalStatus.ACTIVE,
            due_date=due_date
        )
        
        db.add(rental)
        db.commit()
        db.refresh(rental)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RENTAL_CREATED",
            table_name="rentals",
            user_id=admin_user_id,
            record_id=rental.id,
            description=f"대여 생성: {item.name} ({item.serial_number}) - 사용자: {user.student_id}",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 응답 데이터 생성
        rental = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item).joinedload(Item.category)
        ).filter(Rental.id == rental.id).first()
        
        return RentalService._build_rental_response(rental)
    
    @staticmethod
    def return_rental(
        db: Session,
        rental_id: int,
        return_data: RentalReturn,
        admin_user_id: int,
        ip_address: str = None
    ) -> Optional[RentalResponse]:
        """
        대여 반납 처리 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            rental_id: 대여 ID
            return_data: 반납 데이터
            admin_user_id: 관리자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            RentalResponse: 반납된 대여 정보
        """
        rental = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item)
        ).filter(Rental.id == rental_id).first()
        
        if not rental:
            return None
        
        if rental.status not in [RentalStatus.ACTIVE, RentalStatus.OVERDUE]:
            raise ValueError(f"반납 처리할 수 없는 대여 상태입니다 (현재: {rental.status.value})")
        
        # 대여 반납 처리
        rental.status = RentalStatus.RETURNED
        rental.returned_at = datetime.utcnow()
        rental.admin_notes = return_data.admin_notes
        
        # 품목 상태메모 업데이트 및 사용 가능으로 변경
        if return_data.condition_notes:
            rental.notes = f"{rental.notes or ''}\n[반납 상태: {return_data.condition_notes}]".strip()
        
        rental.item.status = ItemStatus.AVAILABLE
        
        db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RENTAL_RETURNED",
            table_name="rentals",
            user_id=admin_user_id,
            record_id=rental.id,
            description=f"대여 반납: {rental.item.name} (사용자: {rental.user.student_id})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return RentalService._build_rental_response(rental)
    
    @staticmethod
    def extend_rental(
        db: Session,
        rental_id: int,
        extend_data: RentalExtend,
        admin_user_id: int,
        ip_address: str = None
    ) -> Optional[RentalResponse]:
        """
        대여 연장 처리 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            rental_id: 대여 ID
            extend_data: 연장 데이터
            admin_user_id: 관리자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            RentalResponse: 연장된 대여 정보
        """
        rental = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item)
        ).filter(Rental.id == rental_id).first()
        
        if not rental:
            return None
        
        if rental.status not in [RentalStatus.ACTIVE, RentalStatus.OVERDUE]:
            raise ValueError(f"연장 처리할 수 없는 대여 상태입니다 (현재: {rental.status.value})")
        
        # 기존 반납 예정일에서 연장
        new_due_date = rental.due_date + timedelta(days=extend_data.extend_days)
        
        # 연장 기록 저장
        old_due_date = rental.due_date
        rental.due_date = new_due_date
        
        # 연체 상태였다면 활성으로 변경
        if rental.status == RentalStatus.OVERDUE:
            rental.status = RentalStatus.ACTIVE
        
        # 연장 사유 기록
        extend_note = f"[연장: {extend_data.extend_days}일 ({old_due_date.strftime('%Y-%m-%d')} → {new_due_date.strftime('%Y-%m-%d')})"
        if extend_data.reason:
            extend_note += f" - 사유: {extend_data.reason}"
        extend_note += "]"
        
        rental.notes = f"{rental.notes or ''}\n{extend_note}".strip()
        
        db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RENTAL_EXTENDED",
            table_name="rentals",
            user_id=admin_user_id,
            record_id=rental.id,
            description=f"대여 연장: {rental.item.name} (사용자: {rental.user.student_id}, {extend_data.extend_days}일)",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return RentalService._build_rental_response(rental)
    
    @staticmethod
    def mark_overdue_rentals(db: Session) -> int:
        """
        연체된 대여들을 일괄 처리 (스케줄러용)
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            int: 연체 처리된 대여 개수
        """
        now = datetime.utcnow()
        
        # 연체된 대여 조회 (ACTIVE 상태에서 반납 예정일 초과)
        overdue_rentals = db.query(Rental).filter(
            and_(
                Rental.status == RentalStatus.ACTIVE,
                Rental.due_date < now
            )
        ).all()
        
        count = 0
        for rental in overdue_rentals:
            # 연체 상태로 변경
            rental.status = RentalStatus.OVERDUE
            
            # 감사 로그 기록
            audit_log = AuditLog.create_log(
                action="RENTAL_OVERDUE",
                table_name="rentals",
                record_id=rental.id,
                description=f"대여 연체: {rental.item.name} (사용자: {rental.user.student_id})"
            )
            db.add(audit_log)
            count += 1
        
        if count > 0:
            db.commit()
        
        return count
    
    @staticmethod
    def get_user_active_rentals(db: Session, user_id: int) -> List[RentalResponse]:
        """
        사용자의 활성 대여 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            List[RentalResponse]: 활성 대여 목록
        """
        rentals = db.query(Rental).options(
            joinedload(Rental.user),
            joinedload(Rental.item).joinedload(Item.category)
        ).filter(
            and_(
                Rental.user_id == user_id,
                Rental.status.in_([RentalStatus.ACTIVE, RentalStatus.OVERDUE])
            )
        ).order_by(Rental.created_at.desc()).all()
        
        return [RentalService._build_rental_response(r) for r in rentals]
    
    @staticmethod
    def get_rental_history(
        db: Session,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RentalHistory]:
        """
        대여 이력 통계 조회 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            user_id: 특정 사용자 ID (선택사항)
            skip: 건너뛸 개수
            limit: 조회할 개수
            
        Returns:
            List[RentalHistory]: 사용자별 대여 이력
        """
        query = db.query(
            User.id.label('user_id'),
            User.name.label('user_name'),
            User.student_id.label('user_student_id'),
            func.count(Rental.id).label('total_rentals'),
            func.sum(func.case([(Rental.status.in_([RentalStatus.ACTIVE, RentalStatus.OVERDUE]), 1)], else_=0)).label('active_rentals'),
            func.sum(func.case([(Rental.status == RentalStatus.OVERDUE, 1)], else_=0)).label('overdue_rentals'),
            func.sum(func.case([(Rental.status == RentalStatus.RETURNED, 1)], else_=0)).label('completed_rentals'),
            func.avg(
                func.case(
                    [(Rental.status == RentalStatus.RETURNED, 
                      func.extract('day', Rental.returned_at - Rental.created_at))],
                    else_=None
                )
            ).label('average_rental_days'),
            func.max(Rental.created_at).label('last_rental_date')
        ).join(Rental, User.id == Rental.user_id).group_by(
            User.id, User.name, User.student_id
        )
        
        if user_id:
            query = query.filter(User.id == user_id)
        
        results = query.order_by(func.count(Rental.id).desc()).offset(skip).limit(limit).all()
        
        history_list = []
        for result in results:
            history_list.append(RentalHistory(
                user_id=result.user_id,
                user_name=result.user_name,
                user_student_id=result.user_student_id,
                total_rentals=result.total_rentals or 0,
                active_rentals=result.active_rentals or 0,
                overdue_rentals=result.overdue_rentals or 0,
                completed_rentals=result.completed_rentals or 0,
                average_rental_days=float(result.average_rental_days) if result.average_rental_days else None,
                last_rental_date=result.last_rental_date
            ))
        
        return history_list
    
    @staticmethod
    def _build_rental_response(rental: Rental) -> RentalResponse:
        """대여 응답 데이터 빌드"""
        now = datetime.utcnow()
        
        # 연체 여부 및 남은/연체 일수 계산
        is_overdue = rental.due_date < now if rental.status in [RentalStatus.ACTIVE, RentalStatus.OVERDUE] else False
        days_remaining = None
        days_overdue = None
        
        if rental.status in [RentalStatus.ACTIVE, RentalStatus.OVERDUE]:
            if is_overdue:
                days_overdue = (now - rental.due_date).days
            else:
                days_remaining = (rental.due_date - now).days
        
        # 총 대여 일수 계산
        if rental.returned_at:
            rental_duration_days = (rental.returned_at - rental.created_at).days
        else:
            rental_duration_days = (now - rental.created_at).days
        
        rental_data = RentalResponse.model_validate(rental)
        
        # 관련 정보 추가
        if rental.user:
            rental_data.user_name = rental.user.name
            rental_data.user_student_id = rental.user.student_id
        
        if rental.item:
            rental_data.item_name = rental.item.name
            rental_data.item_serial_number = rental.item.serial_number
            if rental.item.category:
                rental_data.category_name = rental.item.category.name
        
        # 상태 헬퍼 추가
        rental_data.is_overdue = is_overdue
        rental_data.days_remaining = days_remaining
        rental_data.days_overdue = days_overdue
        rental_data.rental_duration_days = rental_duration_days
        
        return rental_data
    
    @staticmethod
    def get_rental_statistics(db: Session) -> dict:
        """
        대여 통계 조회 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            dict: 대여 통계 정보
        """
        # 전체 대여 개수
        total_rentals = db.query(func.count(Rental.id)).scalar()
        
        # 상태별 대여 개수
        status_counts = db.query(
            Rental.status,
            func.count(Rental.id)
        ).group_by(Rental.status).all()
        
        # 오늘 대여 개수
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_rentals = db.query(func.count(Rental.id)).filter(
            Rental.created_at >= today_start
        ).scalar()
        
        # 현재 활성 대여 개수
        active_rentals = db.query(func.count(Rental.id)).filter(
            Rental.status.in_([RentalStatus.ACTIVE, RentalStatus.OVERDUE])
        ).scalar()
        
        # 연체 대여 개수
        now = datetime.utcnow()
        overdue_rentals = db.query(func.count(Rental.id)).filter(
            and_(
                Rental.status.in_([RentalStatus.ACTIVE, RentalStatus.OVERDUE]),
                Rental.due_date < now
            )
        ).scalar()
        
        # 평균 대여 기간
        avg_rental_days = db.query(
            func.avg(
                func.case(
                    [(Rental.status == RentalStatus.RETURNED,
                      func.extract('day', Rental.returned_at - Rental.created_at))],
                    else_=None
                )
            )
        ).scalar()
        
        return {
            "total_rentals": total_rentals,
            "status_counts": {status.value: count for status, count in status_counts},
            "today_rentals": today_rentals,
            "active_rentals": active_rentals,
            "overdue_rentals": overdue_rentals,
            "average_rental_days": float(avg_rental_days) if avg_rental_days else None
        }