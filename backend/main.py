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
    title="렌탈 관리 시스템",
    description="공과대학 학생회 렌탈 서비스 API",
    version="1.0.0",
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