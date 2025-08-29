from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, or_
from datetime import datetime, timedelta

from app.models.reservation import Reservation
from app.models.item import Item, ItemStatus
from app.models.user import User
from app.models.category import Category
from app.schemas.reservation import (
    ReservationCreate, ReservationUpdate, ReservationResponse, 
    ReservationList, ReservationFilter, ReservationStatus,
    ReservationConfirm, ReservationCancel
)
from app.models.audit_log import AuditLog
from app.core.config import settings


class ReservationService:
    """예약 관리 서비스"""
    
    RESERVATION_DURATION_HOURS = 1  # 예약 유효 시간 (1시간)
    
    @staticmethod
    def get_reservations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ReservationFilter] = None,
        current_user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> ReservationList:
        """
        예약 목록 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            filters: 필터 조건
            current_user_id: 현재 사용자 ID (일반 사용자는 자신 것만)
            is_admin: 관리자 여부
            
        Returns:
            ReservationList: 예약 목록과 통계
        """
        query = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item).joinedload(Item.category)
        )
        
        # 일반 사용자는 자신의 예약만 조회 가능
        if not is_admin and current_user_id:
            query = query.filter(Reservation.user_id == current_user_id)
        
        # 필터 적용
        if filters:
            if filters.user_id and is_admin:  # 관리자만 다른 사용자 필터 가능
                query = query.filter(Reservation.user_id == filters.user_id)
            
            if filters.item_id:
                query = query.filter(Reservation.item_id == filters.item_id)
            
            if filters.category_id:
                query = query.join(Item).filter(Item.category_id == filters.category_id)
            
            if filters.status:
                query = query.filter(Reservation.status == filters.status)
            
            if filters.is_expired is not None:
                now = datetime.utcnow()
                if filters.is_expired:
                    query = query.filter(
                        and_(
                            Reservation.expires_at < now,
                            Reservation.status == ReservationStatus.PENDING
                        )
                    )
                else:
                    query = query.filter(
                        or_(
                            Reservation.expires_at >= now,
                            Reservation.status != ReservationStatus.PENDING
                        )
                    )
            
            if filters.date_from:
                query = query.filter(Reservation.created_at >= filters.date_from)
            
            if filters.date_to:
                query = query.filter(Reservation.created_at <= filters.date_to)
        
        # 총 개수 조회
        total = query.count()
        
        # 페이지네이션 적용하여 예약 조회 (최신 순)
        reservations = query.order_by(Reservation.created_at.desc()).offset(skip).limit(limit).all()
        
        # 예약 응답 데이터 생성
        reservation_responses = []
        for reservation in reservations:
            reservation_data = ReservationService._build_reservation_response(reservation)
            reservation_responses.append(reservation_data)
        
        # 상태별 통계 조회
        stats_base_query = db.query(Reservation.status, func.count(Reservation.id)).group_by(Reservation.status)
        if not is_admin and current_user_id:
            stats_base_query = stats_base_query.filter(Reservation.user_id == current_user_id)
        
        status_stats = dict(stats_base_query.all())
        
        return ReservationList(
            reservations=reservation_responses,
            total=total,
            pending_count=status_stats.get(ReservationStatus.PENDING, 0),
            confirmed_count=status_stats.get(ReservationStatus.CONFIRMED, 0),
            cancelled_count=status_stats.get(ReservationStatus.CANCELLED, 0),
            expired_count=status_stats.get(ReservationStatus.EXPIRED, 0)
        )
    
    @staticmethod
    def get_reservation(
        db: Session, 
        reservation_id: int,
        current_user_id: Optional[int] = None,
        is_admin: bool = False
    ) -> Optional[ReservationResponse]:
        """
        특정 예약 조회
        
        Args:
            db: 데이터베이스 세션
            reservation_id: 예약 ID
            current_user_id: 현재 사용자 ID
            is_admin: 관리자 여부
            
        Returns:
            ReservationResponse: 예약 정보
        """
        query = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item).joinedload(Item.category)
        ).filter(Reservation.id == reservation_id)
        
        # 일반 사용자는 자신의 예약만 조회 가능
        if not is_admin and current_user_id:
            query = query.filter(Reservation.user_id == current_user_id)
        
        reservation = query.first()
        if not reservation:
            return None
        
        return ReservationService._build_reservation_response(reservation)
    
    @staticmethod
    def create_reservation(
        db: Session,
        reservation_data: ReservationCreate,
        user_id: int,
        ip_address: str = None
    ) -> ReservationResponse:
        """
        새 예약 생성
        
        Args:
            db: 데이터베이스 세션
            reservation_data: 예약 생성 데이터
            user_id: 사용자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            ReservationResponse: 생성된 예약 정보
            
        Raises:
            ValueError: 예약 불가능한 경우
        """
        # 품목 존재 및 예약 가능 여부 확인
        item = db.query(Item).options(joinedload(Item.category)).filter(
            and_(
                Item.id == reservation_data.item_id,
                Item.is_active == True
            )
        ).first()
        
        if not item:
            raise ValueError("존재하지 않거나 비활성화된 품목입니다")
        
        if item.status != ItemStatus.AVAILABLE:
            raise ValueError(f"현재 예약할 수 없는 품목입니다 (상태: {item.status.value})")
        
        # 사용자의 현재 활성 예약 개수 확인 (제한 없음이지만 확인용)
        active_reservations = db.query(func.count(Reservation.id)).filter(
            and_(
                Reservation.user_id == user_id,
                Reservation.status == ReservationStatus.PENDING
            )
        ).scalar()
        
        # 같은 품목에 대한 중복 예약 방지
        existing_reservation = db.query(Reservation).filter(
            and_(
                Reservation.user_id == user_id,
                Reservation.item_id == reservation_data.item_id,
                Reservation.status == ReservationStatus.PENDING
            )
        ).first()
        
        if existing_reservation:
            raise ValueError("이미 해당 품목을 예약하였습니다")
        
        # 예약 만료 시간 계산 (1시간 후)
        expires_at = datetime.utcnow() + timedelta(hours=ReservationService.RESERVATION_DURATION_HOURS)
        
        # 새 예약 생성
        reservation = Reservation(
            user_id=user_id,
            item_id=reservation_data.item_id,
            notes=reservation_data.notes,
            status=ReservationStatus.PENDING,
            expires_at=expires_at
        )
        
        # 품목 상태를 예약됨으로 변경
        item.status = ItemStatus.RESERVED
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RESERVATION_CREATED",
            table_name="reservations",
            user_id=user_id,
            record_id=reservation.id,
            description=f"예약 생성: {item.name} ({item.serial_number})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        # 응답 데이터 생성
        reservation = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item).joinedload(Item.category)
        ).filter(Reservation.id == reservation.id).first()
        
        return ReservationService._build_reservation_response(reservation)
    
    @staticmethod
    def confirm_reservation(
        db: Session,
        reservation_id: int,
        confirm_data: ReservationConfirm,
        admin_user_id: int,
        ip_address: str = None
    ) -> Optional[ReservationResponse]:
        """
        예약 수령 확인 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            reservation_id: 예약 ID
            confirm_data: 확인 데이터
            admin_user_id: 관리자 ID
            ip_address: 클라이언트 IP
            
        Returns:
            ReservationResponse: 확인된 예약 정보
        """
        reservation = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item)
        ).filter(Reservation.id == reservation_id).first()
        
        if not reservation:
            return None
        
        if reservation.status != ReservationStatus.PENDING:
            raise ValueError(f"수령 확인할 수 없는 예약 상태입니다 (현재: {reservation.status.value})")
        
        # 예약 상태 업데이트
        reservation.status = ReservationStatus.CONFIRMED
        reservation.confirmed_at = datetime.utcnow()
        reservation.admin_notes = confirm_data.admin_notes
        
        # 품목 상태를 대여중으로 변경
        reservation.item.status = ItemStatus.RENTED
        
        db.commit()
        
        # 대여 레코드 자동 생성
        from app.services.rental_service import RentalService
        from app.schemas.rental import RentalCreate
        
        try:
            rental_data = RentalCreate(
                item_id=reservation.item_id,
                reservation_id=reservation.id,
                notes=f"예약 확인을 통한 자동 대여 생성"
            )
            
            RentalService.create_rental(
                db=db,
                rental_data=rental_data,
                user_id=reservation.user_id,
                admin_user_id=admin_user_id,
                ip_address=ip_address
            )
        except Exception as e:
            # 대여 레코드 생성 실패 시 롤백하지 않고 로그만 기록
            audit_log = AuditLog.create_log(
                action="RENTAL_CREATE_FAILED",
                table_name="reservations",
                user_id=admin_user_id,
                record_id=reservation.id,
                description=f"예약 확인 후 대여 레코드 생성 실패: {str(e)}",
                ip_address=ip_address
            )
            db.add(audit_log)
            db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RESERVATION_CONFIRMED",
            table_name="reservations",
            user_id=admin_user_id,
            record_id=reservation.id,
            description=f"예약 수령 확인: {reservation.item.name} (사용자: {reservation.user.student_id})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return ReservationService._build_reservation_response(reservation)
    
    @staticmethod
    def cancel_reservation(
        db: Session,
        reservation_id: int,
        cancel_data: ReservationCancel,
        user_id: int,
        is_admin: bool = False,
        ip_address: str = None
    ) -> Optional[ReservationResponse]:
        """
        예약 취소
        
        Args:
            db: 데이터베이스 세션
            reservation_id: 예약 ID
            cancel_data: 취소 데이터
            user_id: 사용자 ID
            is_admin: 관리자 여부
            ip_address: 클라이언트 IP
            
        Returns:
            ReservationResponse: 취소된 예약 정보
        """
        query = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item)
        ).filter(Reservation.id == reservation_id)
        
        # 일반 사용자는 자신의 예약만 취소 가능
        if not is_admin:
            query = query.filter(Reservation.user_id == user_id)
        
        reservation = query.first()
        if not reservation:
            return None
        
        if reservation.status not in [ReservationStatus.PENDING]:
            raise ValueError(f"취소할 수 없는 예약 상태입니다 (현재: {reservation.status.value})")
        
        # 예약 취소 처리
        reservation.status = ReservationStatus.CANCELLED
        reservation.cancelled_at = datetime.utcnow()
        if cancel_data.reason:
            reservation.notes = f"{reservation.notes or ''}\n[취소 사유: {cancel_data.reason}]".strip()
        
        # 품목 상태를 사용 가능으로 복원
        reservation.item.status = ItemStatus.AVAILABLE
        
        db.commit()
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="RESERVATION_CANCELLED",
            table_name="reservations",
            user_id=user_id,
            record_id=reservation.id,
            description=f"예약 취소: {reservation.item.name} (사용자: {reservation.user.student_id})",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return ReservationService._build_reservation_response(reservation)
    
    @staticmethod
    def expire_reservations(db: Session) -> int:
        """
        만료된 예약들을 일괄 처리 (스케줄러용)
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            int: 만료 처리된 예약 개수
        """
        now = datetime.utcnow()
        
        # 만료된 예약 조회
        expired_reservations = db.query(Reservation).options(
            joinedload(Reservation.item)
        ).filter(
            and_(
                Reservation.status == ReservationStatus.PENDING,
                Reservation.expires_at < now
            )
        ).all()
        
        count = 0
        for reservation in expired_reservations:
            # 예약 만료 처리
            reservation.status = ReservationStatus.EXPIRED
            
            # 품목 상태를 사용 가능으로 복원
            reservation.item.status = ItemStatus.AVAILABLE
            
            # 감사 로그 기록
            audit_log = AuditLog.create_log(
                action="RESERVATION_EXPIRED",
                table_name="reservations",
                record_id=reservation.id,
                description=f"예약 자동 만료: {reservation.item.name}"
            )
            db.add(audit_log)
            count += 1
        
        if count > 0:
            db.commit()
        
        return count
    
    @staticmethod
    def get_user_active_reservations(db: Session, user_id: int) -> List[ReservationResponse]:
        """
        사용자의 활성 예약 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            List[ReservationResponse]: 활성 예약 목록
        """
        reservations = db.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.item).joinedload(Item.category)
        ).filter(
            and_(
                Reservation.user_id == user_id,
                Reservation.status == ReservationStatus.PENDING
            )
        ).order_by(Reservation.created_at.desc()).all()
        
        return [ReservationService._build_reservation_response(r) for r in reservations]
    
    @staticmethod
    def _build_reservation_response(reservation: Reservation) -> ReservationResponse:
        """예약 응답 데이터 빌드"""
        now = datetime.utcnow()
        
        # 만료 여부 및 남은 시간 계산
        is_expired = reservation.expires_at < now if reservation.status == ReservationStatus.PENDING else False
        remaining_minutes = None
        if reservation.status == ReservationStatus.PENDING and not is_expired:
            remaining_minutes = int((reservation.expires_at - now).total_seconds() / 60)
        
        # 활성 상태 계산
        is_active = reservation.status == ReservationStatus.PENDING and not is_expired
        
        reservation_data = ReservationResponse.model_validate(reservation)
        
        # 관련 정보 추가
        if reservation.user:
            reservation_data.user_name = reservation.user.name
            reservation_data.user_student_id = reservation.user.student_id
        
        if reservation.item:
            reservation_data.item_name = reservation.item.name
            reservation_data.item_serial_number = reservation.item.serial_number
            if reservation.item.category:
                reservation_data.category_name = reservation.item.category.name
        
        # 상태 헬퍼 추가
        reservation_data.is_active = is_active
        reservation_data.is_expired = is_expired
        reservation_data.remaining_minutes = remaining_minutes
        
        return reservation_data
    
    @staticmethod
    def get_reservation_statistics(db: Session) -> dict:
        """
        예약 통계 조회 (관리자용)
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            dict: 예약 통계 정보
        """
        # 전체 예약 개수
        total_reservations = db.query(func.count(Reservation.id)).scalar()
        
        # 상태별 예약 개수
        status_counts = db.query(
            Reservation.status,
            func.count(Reservation.id)
        ).group_by(Reservation.status).all()
        
        # 오늘 예약 개수
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_reservations = db.query(func.count(Reservation.id)).filter(
            Reservation.created_at >= today_start
        ).scalar()
        
        # 현재 활성 예약 개수 (만료되지 않은 PENDING)
        now = datetime.utcnow()
        active_reservations = db.query(func.count(Reservation.id)).filter(
            and_(
                Reservation.status == ReservationStatus.PENDING,
                Reservation.expires_at >= now
            )
        ).scalar()
        
        return {
            "total_reservations": total_reservations,
            "status_counts": {status.value: count for status, count in status_counts},
            "today_reservations": today_reservations,
            "active_reservations": active_reservations
        }