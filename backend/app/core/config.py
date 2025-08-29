from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://rental_user:rental_password@postgres:5432/rental_db"
    REDIS_URL: str = "redis://redis:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # School API
    SCHOOL_API_BASE_URL: str = "https://your-school-api.ac.kr"
    SCHOOL_API_LOGIN_ENDPOINT: str = "/login"
    SCHOOL_API_TIMEOUT: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Application
    DEBUG: bool = True
    
    # 공대 전공 리스트 (TODO: 실제 전공명으로 업데이트)
    ENGINEERING_MAJORS: List[str] = [
        "컴퓨터과학전공",
        "전자공학과",
        "기계공학과",
        "화학공학과",
        "건설환경공학과",
        "산업공학과"
    ]

    class Config:
        env_file = ".env"


settings = Settings()