from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta, date
import enum

from app.db.database import Base


class RentalStatus(enum.Enum):
    """대여 상태 Enum"""
    ACTIVE = "ACTIVE"       # 대여 중
    RETURNED = "RETURNED"   # 반납 완료
    OVERDUE = "OVERDUE"     # 연체


class Rental(Base):
    """대여 테이블"""
    __tablename__ = "rentals"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="대여 ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="사용자 ID")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="품목 ID")
    
    # 대여 시간 정보
    rental_date = Column(Date, default=date.today, nullable=False, comment="대여 일자")
    due_date = Column(Date, nullable=False, comment="반납 예정 일자")
    return_date = Column(Date, nullable=True, comment="실제 반납 일자")
    
    # 상태
    status = Column(Enum(RentalStatus), default=RentalStatus.ACTIVE, nullable=False, index=True, comment="대여 상태")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    
    # 관계 설정
    user = relationship("User", back_populates="rentals")
    item = relationship("Item", back_populates="rentals")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 대여 생성 시 자동으로 7일 후 반납 예정일 설정
        if not self.due_date:
            rental_date = self.rental_date or date.today()
            self.due_date = rental_date + timedelta(days=7)
    
    def __repr__(self):
        return f"<Rental(id={self.id}, user_id={self.user_id}, item_id={self.item_id}, status='{self.status.value}')>"
    
    @property
    def is_active(self) -> bool:
        """활성 대여 여부"""
        return self.status == RentalStatus.ACTIVE
    
    @property
    def is_overdue(self) -> bool:
        """연체 여부 확인"""
        if self.status != RentalStatus.ACTIVE:
            return False
        return date.today() > self.due_date
    
    @property
    def days_overdue(self) -> int:
        """연체 일수"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    @property
    def days_remaining(self) -> int:
        """남은 대여 일수"""
        if self.status != RentalStatus.ACTIVE:
            return 0
        remaining = (self.due_date - date.today()).days
        return max(0, remaining)
    
    @property
    def rental_duration(self) -> int:
        """실제 대여 기간 (일수)"""
        end_date = self.return_date or date.today()
        return (end_date - self.rental_date).days
    
    def return_item(self) -> bool:
        """품목 반납 처리"""
        if self.status != RentalStatus.ACTIVE:
            return False
        
        self.return_date = date.today()
        self.status = RentalStatus.RETURNED
        return True