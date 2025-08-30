from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    student_id: str = Field(..., description="학번")
    name: str = Field(..., description="이름")
    department: str = Field(..., description="학과/전공")
    email: Optional[EmailStr] = Field(None, description="이메일")
    phone: Optional[str] = Field(None, description="전화번호")


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, description="비밀번호")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="이름")
    email: Optional[EmailStr] = Field(None, description="이메일")
    phone: Optional[str] = Field(None, description="전화번호")
    is_active: Optional[bool] = Field(None, description="활성 상태")


class UserInDB(UserBase):
    id: int
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """사용자 정보 응답 스키마 (민감 정보 제외)"""
    pass


class UserProfile(User):
    """프로필 정보 스키마 (추가 정보 포함)"""
    total_rentals: Optional[int] = Field(None, description="총 대여 횟수")
    active_rentals: Optional[int] = Field(None, description="현재 대여 중인 품목 수")
    total_reservations: Optional[int] = Field(None, description="총 예약 횟수")


class UserList(BaseModel):
    """사용자 목록 스키마"""
    users: list[User]
    total: int
    page: int
    page_size: int


class UserStatistics(BaseModel):
    """사용자 통계 스키마"""
    total_users: int
    active_users: int
    total_students: int
    total_admins: int
    users_with_active_rentals: int
    users_with_overdue_rentals: int