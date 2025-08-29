from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any

from app.db.database import Base


class AuditLog(Base):
    """감사 로그 테이블"""
    __tablename__ = "audit_logs"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, comment="로그 ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="사용자 ID (시스템 작업시 NULL 가능)")
    
    # 작업 정보
    action = Column(String(100), nullable=False, index=True, comment="수행된 작업 (CREATE, UPDATE, DELETE 등)")
    table_name = Column(String(100), nullable=False, index=True, comment="대상 테이블명")
    record_id = Column(Integer, nullable=True, index=True, comment="대상 레코드 ID")
    
    # 변경 내용
    changes = Column(JSON, nullable=True, comment="변경된 내용 (before/after)")
    description = Column(Text, nullable=True, comment="작업 설명")
    
    # 시스템 정보
    ip_address = Column(String(45), nullable=True, comment="클라이언트 IP 주소")
    user_agent = Column(Text, nullable=True, comment="사용자 에이전트")
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="로그 생성 시간")
    
    # 관계 설정
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', table='{self.table_name}', record_id={self.record_id})>"
    
    @classmethod
    def create_log(
        cls,
        action: str,
        table_name: str,
        user_id: Optional[int] = None,
        record_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> "AuditLog":
        """감사 로그 생성 헬퍼 메서드"""
        return cls(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            changes=changes,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @property
    def is_system_action(self) -> bool:
        """시스템 작업 여부 (사용자 ID가 없는 경우)"""
        return self.user_id is None
    
    @property
    def formatted_changes(self) -> str:
        """변경 내용을 읽기 쉬운 형태로 포맷"""
        if not self.changes:
            return "변경사항 없음"
        
        formatted = []
        for key, value in self.changes.items():
            if isinstance(value, dict) and 'before' in value and 'after' in value:
                formatted.append(f"{key}: {value['before']} → {value['after']}")
            else:
                formatted.append(f"{key}: {value}")
        
        return ", ".join(formatted)