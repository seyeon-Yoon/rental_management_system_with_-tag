from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

# PostgreSQL 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base 클래스 생성
Base = declarative_base()


# 데이터베이스 세션 의존성
def get_db():
    """데이터베이스 세션을 가져오는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_tables():
    """테이블 생성 함수"""
    # 모든 모델 import (테이블 생성을 위해)
    from app.models.user import User
    from app.models.category import Category
    from app.models.item import Item
    from app.models.reservation import Reservation
    from app.models.rental import Rental
    from app.models.audit_log import AuditLog
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    print("데이터베이스 테이블이 생성되었습니다.")


async def init_db():
    """데이터베이스 초기화"""
    await create_tables()
    print("데이터베이스 초기화가 완료되었습니다.")