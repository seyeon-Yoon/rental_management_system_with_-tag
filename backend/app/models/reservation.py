from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum

from app.db.database import Base


class ReservationStatus(enum.Enum):
    """예약 상태 Enum"""
    PENDING = "PENDING"       # 대기 중 (예약 완료, 수령 대기)
    CONFIRMED = "CONFIRMED"   # 확인됨 (대여로 전환됨)
    EXPIRED = "EXPIRED"       # 만료됨 (1시간 초과)
    CANCELLED = "CANCELLED"   # 취소됨


class Reservation(Base):
    """예약 테이블"""
    __tablename__ = "reservations"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="예약 ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="사용자 ID")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="품목 ID")
    
    # 예약 시간 정보
    reserved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="예약 시간")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="만료 시간")
    
    # 상태
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False, index=True, comment="예약 상태")
    
    # 예약 메모
    notes = Column(String(500), nullable=True, comment="예약 메모")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    
    # 관계 설정
    user = relationship("User", back_populates="reservations")
    item = relationship("Item", back_populates="reservations")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 예약 생성 시 자동으로 1시간 후 만료 시간 설정
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=1)
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, user_id={self.user_id}, item_id={self.item_id}, status='{self.status.value}')>"
    
    @property
    def is_active(self) -> bool:
        """활성 예약 여부 (PENDING 상태)"""
        return self.status == ReservationStatus.PENDING
    
    @property
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def remaining_time(self) -> timedelta:
        """남은 시간"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    @property
    def remaining_minutes(self) -> int:
        """남은 시간 (분 단위)"""
        remaining = self.remaining_time
        return max(0, int(remaining.total_seconds() // 60))