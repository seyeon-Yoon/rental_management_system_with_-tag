from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://rental_user:rental_password@postgres:5432/rental_db"
    REDIS_URL: str = "redis://redis:6379"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # University API
    UNIVERSITY_API_BASE_URL: str = "https://your-university-api.ac.kr"
    UNIVERSITY_API_LOGIN_ENDPOINT: str = "/login"
    UNIVERSITY_API_TIMEOUT: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Application
    DEBUG: bool = True
    
    # 상명대학교 융합공과대학 전공 리스트 (2024년 기준)
    CONVERGENCE_ENGINEERING_MAJORS: List[str] = [
        # 지능·데이터 융합학부
        "휴먼지능정보공학전공",
        "핀테크전공", 
        "빅데이터융합전공",
        "스마트생산전공",
        
        # SW융합학부
        "컴퓨터과학전공",
        "전기공학전공",
        "지능IOT융합전공", 
        "융합전자공학전공",
        "게임전공",
        "애니메이션전공",
        "한일문화콘텐츠전공",
        
        # 생명화학공학부
        "생명공학전공",
        "화학에너지공학전공",
        "화공신소재전공"
    ]

    class Config:
        env_file = "../.env"
        extra = "ignore"  # 추가 변수 무시


settings = Settings()