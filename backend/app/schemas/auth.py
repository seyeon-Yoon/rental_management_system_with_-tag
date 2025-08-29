from pydantic import BaseModel, Field
from typing import Optional
from app.models.user import UserRole


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    student_id: str = Field(..., min_length=1, max_length=20, description="학번")
    password: str = Field(..., min_length=1, description="비밀번호")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "202210950",
                "password": "your-password"
            }
        }


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: int
    student_id: str
    name: str
    department: str
    email: Optional[str] = None
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": "202210950",
                "name": "윤세연",
                "department": "컴퓨터과학전공",
                "email": "student@university.ac.kr",
                "role": "STUDENT",
                "is_active": True
            }
        }


class LoginResponse(BaseModel):
    """로그인 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "student_id": "202210950",
                    "name": "윤세연",
                    "department": "컴퓨터과학전공",
                    "email": "student@university.ac.kr",
                    "role": "STUDENT",
                    "is_active": True
                }
            }
        }


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: str = Field(..., description="갱신용 토큰")


class LogoutResponse(BaseModel):
    """로그아웃 응답 스키마"""
    message: str = "로그아웃 되었습니다"
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "로그아웃 되었습니다"
            }
        }