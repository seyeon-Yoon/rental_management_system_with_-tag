from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Category(Base):
    """카테고리 테이블"""
    __tablename__ = "categories"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="카테고리 ID")
    name = Column(String(100), unique=True, nullable=False, index=True, comment="카테고리 이름")
    description = Column(Text, nullable=True, comment="카테고리 설명")
    
    # 상태
    is_active = Column(Boolean, default=True, nullable=False, comment="활성 상태")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 시간")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="수정 시간")
    
    # 관계 설정
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
    
    @property
    def active_items_count(self) -> int:
        """활성 품목 개수"""
        return len([item for item in self.items if item.is_active])