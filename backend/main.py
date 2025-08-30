from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await create_tables()
    print("Database tables created")
    yield
    # Shutdown
    print("Application shutdown")


app = FastAPI(
    title="렌탈 관리 시스템 API",
    description="""
    ## 융합공과대학 학생회 렌탈 서비스 관리 시스템

    ### 주요 기능
    - **인증 시스템**: 대학교 API 연동을 통한 학생 인증
    - **품목 관리**: 카테고리별 품목 등록, 수정, 삭제, 재고 관리
    - **예약 시스템**: 온라인 예약, 1시간 제한, 자동 만료
    - **대여 관리**: 7일 대여 기간, 연장, 반납, 연체 처리

    ### API 구조
    - `/auth`: 인증 관련 (로그인, 로그아웃, 토큰 관리)
    - `/categories`: 카테고리 관리
    - `/items`: 품목 관리
    - `/reservations`: 예약 관리
    - `/rentals`: 대여 관리

    ### 권한 구조
    - **학생**: 품목 조회, 예약 생성/취소, 본인 대여 이력 조회
    - **관리자**: 모든 기능 + 품목 등록/수정/삭제, 예약 확인, 대여 반납/연장

    ### 개발 정보
    - **Backend**: FastAPI + PostgreSQL + Redis
    - **Frontend**: React + TypeScript + Material-UI
    - **Authentication**: JWT Token + Redis Session
    """,
    version="1.0.0",
    contact={
        "name": "융합공과대학 학생회",
        "email": "contact@example.com"
    },
    license_info={
        "name": "MIT License"
    },
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "렌탈 관리 시스템이 정상 작동 중입니다."}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "공과대학 렌탈 관리 시스템 API", "version": "1.0.0"}