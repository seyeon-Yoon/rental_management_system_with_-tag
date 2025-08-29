from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class ItemStatus(enum.Enum):
    """품목 상태 Enum"""
    AVAILABLE = "AVAILABLE"      # 대여 가능
    RESERVED = "RESERVED"        # 예약됨
    RENTED = "RENTED"           # 대여 중
    MAINTENANCE = "MAINTENANCE"  # 정비 중


class Item(Base):
    """품목 테이블"""
    __tablename__ = "items"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="품목 ID")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True, comment="카테고리 ID")
    name = Column(String(200), nullable=False, index=True, comment="품목 이름")
    description = Column(Text, nullable=True, comment="품목 설명")
    serial_number = Column(String(100), unique=True, nullable=False, index=True, comment="시리얼 번호")
    
    # 상태
    status = Column(Enum(ItemStatus), default=ItemStatus.AVAILABLE, nullable=False, index=True, comment="품목 상태")
    is_active = Column(Boolean, default=True, nullable=False, comment="활성 상태")
    
    # 메타데이터 (JSONB - 품목별 특수 속성)
    item_metadata = Column(JSON, nullable=True, comment="메타데이터 (색상, 크기, 모델명 등)")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    
    # 관계 설정
    category = relationship("Category", back_populates="items")
    reservations = relationship("Reservation", back_populates="item", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', serial='{self.serial_number}', status='{self.status.value}')>"
    
    @property
    def is_available(self) -> bool:
        """대여 가능 여부"""
        return self.status == ItemStatus.AVAILABLE and self.is_active
    
    @property
    def is_reserved(self) -> bool:
        """예약 상태 여부"""
        return self.status == ItemStatus.RESERVED
    
    @property
    def is_rented(self) -> bool:
        """대여 중 여부"""
        return self.status == ItemStatus.RENTED
    
    @property
    def current_reservation(self):
        """현재 활성 예약"""
        from app.models.reservation import ReservationStatus
        return next((r for r in self.reservations if r.status == ReservationStatus.PENDING), None)
    
    @property
    def current_rental(self):
        """현재 활성 대여"""
        from app.models.rental import RentalStatus
        return next((r for r in self.rentals if r.status == RentalStatus.ACTIVE), None)