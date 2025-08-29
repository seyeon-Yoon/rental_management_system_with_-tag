from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class UserRole(enum.Enum):
    """사용자 역할 Enum"""
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="사용자 ID")
    student_id = Column(String(20), unique=True, index=True, nullable=False, comment="학번")
    name = Column(String(50), nullable=False, comment="이름")
    department = Column(String(100), nullable=False, comment="학과")
    email = Column(String(100), nullable=True, comment="이메일")
    
    # 권한 및 상태
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False, comment="사용자 역할")
    is_active = Column(Boolean, default=True, nullable=False, comment="활성 상태")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="마지막 로그인 시간")
    
    # 관계 설정
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")
    rentals = relationship("Rental", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, student_id='{self.student_id}', name='{self.name}')>"
    
    @property
    def is_admin(self) -> bool:
        """관리자 여부 확인"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_student(self) -> bool:
        """학생 여부 확인"""
        return self.role == UserRole.STUDENT