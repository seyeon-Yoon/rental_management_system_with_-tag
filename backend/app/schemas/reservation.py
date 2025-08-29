from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReservationStatus(str, Enum):
    """예약 상태"""
    PENDING = "PENDING"      # 예약 대기 (1시간 내 수령 필요)
    CONFIRMED = "CONFIRMED"  # 수령 완료 (대여로 전환)
    CANCELLED = "CANCELLED"  # 예약 취소
    EXPIRED = "EXPIRED"      # 예약 만료 (1시간 초과)


class ReservationBase(BaseModel):
    """예약 기본 스키마"""
    item_id: int = Field(..., description="품목 ID")
    notes: Optional[str] = Field(None, max_length=500, description="예약 메모")


class ReservationCreate(ReservationBase):
    """예약 생성 스키마"""
    pass
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": 1,
                "notes": "오후 3시경 수령 예정입니다."
            }
        }


class ReservationUpdate(BaseModel):
    """예약 수정 스키마 (관리자용)"""
    status: Optional[ReservationStatus] = Field(None, description="예약 상태")
    notes: Optional[str] = Field(None, max_length=500, description="예약 메모")
    admin_notes: Optional[str] = Field(None, max_length=500, description="관리자 메모")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "CONFIRMED",
                "admin_notes": "학생회실에서 수령 완료"
            }
        }


class ReservationResponse(ReservationBase):
    """예약 응답 스키마"""
    id: int
    user_id: int
    status: ReservationStatus
    expires_at: datetime
    admin_notes: Optional[str] = Field(None, description="관리자 메모")
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = Field(None, description="수령 확인 시간")
    cancelled_at: Optional[datetime] = Field(None, description="취소 시간")
    
    # 관련 정보
    user_name: Optional[str] = Field(None, description="예약자 이름")
    user_student_id: Optional[str] = Field(None, description="예약자 학번")
    item_name: Optional[str] = Field(None, description="품목명")
    item_serial_number: Optional[str] = Field(None, description="품목 일련번호")
    category_name: Optional[str] = Field(None, description="카테고리명")
    
    # 상태 헬퍼
    is_active: Optional[bool] = Field(None, description="활성 예약 여부")
    is_expired: Optional[bool] = Field(None, description="만료 여부")
    remaining_minutes: Optional[int] = Field(None, description="남은 시간(분)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "item_id": 1,
                "status": "PENDING",
                "notes": "오후 3시경 수령 예정입니다.",
                "admin_notes": None,
                "expires_at": "2025-08-29T15:00:00Z",
                "created_at": "2025-08-29T14:00:00Z",
                "updated_at": "2025-08-29T14:00:00Z",
                "confirmed_at": None,
                "cancelled_at": None,
                "user_name": "김학생",
                "user_student_id": "202210950",
                "item_name": "보조배터리",
                "item_serial_number": "PWR001",
                "category_name": "전자기기",
                "is_active": True,
                "is_expired": False,
                "remaining_minutes": 45
            }
        }


class ReservationList(BaseModel):
    """예약 목록 응답 스키마"""
    reservations: list[ReservationResponse]
    total: int
    pending_count: int
    confirmed_count: int
    cancelled_count: int
    expired_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "reservations": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "item_id": 1,
                        "status": "PENDING",
                        "notes": "오후 수령 예정",
                        "expires_at": "2025-08-29T15:00:00Z",
                        "created_at": "2025-08-29T14:00:00Z",
                        "updated_at": "2025-08-29T14:00:00Z",
                        "user_name": "김학생",
                        "item_name": "보조배터리",
                        "is_active": True,
                        "remaining_minutes": 45
                    }
                ],
                "total": 15,
                "pending_count": 8,
                "confirmed_count": 3,
                "cancelled_count": 2,
                "expired_count": 2
            }
        }


class ReservationFilter(BaseModel):
    """예약 필터 스키마"""
    user_id: Optional[int] = Field(None, description="사용자 ID로 필터링")
    item_id: Optional[int] = Field(None, description="품목 ID로 필터링")
    category_id: Optional[int] = Field(None, description="카테고리 ID로 필터링")
    status: Optional[ReservationStatus] = Field(None, description="상태로 필터링")
    is_expired: Optional[bool] = Field(None, description="만료 여부로 필터링")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "status": "PENDING",
                "is_expired": False,
                "date_from": "2025-08-29T00:00:00Z",
                "date_to": "2025-08-29T23:59:59Z"
            }
        }


class ReservationConfirm(BaseModel):
    """예약 수령 확인 스키마 (관리자용)"""
    admin_notes: Optional[str] = Field(None, max_length=500, description="수령 확인 메모")
    
    class Config:
        json_schema_extra = {
            "example": {
                "admin_notes": "학생회실에서 정상 수령 완료"
            }
        }


class ReservationCancel(BaseModel):
    """예약 취소 스키마"""
    reason: Optional[str] = Field(None, max_length=500, description="취소 사유")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "개인 사정으로 인한 취소"
            }
        }