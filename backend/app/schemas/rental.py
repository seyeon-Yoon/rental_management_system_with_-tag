from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RentalStatus(str, Enum):
    """대여 상태"""
    ACTIVE = "ACTIVE"        # 대여 중
    RETURNED = "RETURNED"    # 반납 완료
    OVERDUE = "OVERDUE"      # 연체
    LOST = "LOST"           # 분실


class RentalBase(BaseModel):
    """대여 기본 스키마"""
    item_id: int = Field(..., description="품목 ID")
    notes: Optional[str] = Field(None, max_length=500, description="대여 메모")


class RentalCreate(RentalBase):
    """대여 생성 스키마 (관리자용 - 예약 확인 시 자동 생성)"""
    reservation_id: Optional[int] = Field(None, description="연결된 예약 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": 1,
                "reservation_id": 1,
                "notes": "정상 대여 처리"
            }
        }


class RentalUpdate(BaseModel):
    """대여 수정 스키마 (관리자용)"""
    status: Optional[RentalStatus] = Field(None, description="대여 상태")
    notes: Optional[str] = Field(None, max_length=500, description="대여 메모")
    admin_notes: Optional[str] = Field(None, max_length=500, description="관리자 메모")
    due_date: Optional[datetime] = Field(None, description="반납 예정일")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "RETURNED",
                "admin_notes": "정상 반납 확인",
                "notes": "사용 상태 양호"
            }
        }


class RentalReturn(BaseModel):
    """대여 반납 스키마 (관리자용)"""
    admin_notes: Optional[str] = Field(None, max_length=500, description="반납 확인 메모")
    condition_notes: Optional[str] = Field(None, max_length=500, description="품목 상태 메모")
    
    class Config:
        json_schema_extra = {
            "example": {
                "admin_notes": "정상 반납 처리 완료",
                "condition_notes": "사용 흔적 없음, 상태 양호"
            }
        }


class RentalResponse(RentalBase):
    """대여 응답 스키마"""
    id: int
    user_id: int
    reservation_id: Optional[int] = Field(None, description="연결된 예약 ID")
    status: RentalStatus
    due_date: datetime
    admin_notes: Optional[str] = Field(None, description="관리자 메모")
    created_at: datetime
    updated_at: datetime
    returned_at: Optional[datetime] = Field(None, description="반납 시간")
    
    # 관련 정보
    user_name: Optional[str] = Field(None, description="대여자 이름")
    user_student_id: Optional[str] = Field(None, description="대여자 학번")
    item_name: Optional[str] = Field(None, description="품목명")
    item_serial_number: Optional[str] = Field(None, description="품목 일련번호")
    category_name: Optional[str] = Field(None, description="카테고리명")
    
    # 상태 헬퍼
    is_overdue: Optional[bool] = Field(None, description="연체 여부")
    days_remaining: Optional[int] = Field(None, description="남은 일수")
    days_overdue: Optional[int] = Field(None, description="연체 일수")
    rental_duration_days: Optional[int] = Field(None, description="총 대여 일수")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "item_id": 1,
                "reservation_id": 1,
                "status": "ACTIVE",
                "notes": "정상 대여 처리",
                "admin_notes": "학생회실에서 수령 확인",
                "due_date": "2025-09-05T14:00:00Z",
                "created_at": "2025-08-29T14:00:00Z",
                "updated_at": "2025-08-29T14:00:00Z",
                "returned_at": None,
                "user_name": "김학생",
                "user_student_id": "202210950",
                "item_name": "보조배터리",
                "item_serial_number": "PWR001",
                "category_name": "전자기기",
                "is_overdue": False,
                "days_remaining": 7,
                "days_overdue": None,
                "rental_duration_days": 0
            }
        }


class RentalList(BaseModel):
    """대여 목록 응답 스키마"""
    rentals: list[RentalResponse]
    total: int
    active_count: int
    returned_count: int
    overdue_count: int
    lost_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "rentals": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "item_id": 1,
                        "status": "ACTIVE",
                        "due_date": "2025-09-05T14:00:00Z",
                        "created_at": "2025-08-29T14:00:00Z",
                        "user_name": "김학생",
                        "item_name": "보조배터리",
                        "is_overdue": False,
                        "days_remaining": 7
                    }
                ],
                "total": 25,
                "active_count": 15,
                "returned_count": 8,
                "overdue_count": 2,
                "lost_count": 0
            }
        }


class RentalFilter(BaseModel):
    """대여 필터 스키마"""
    user_id: Optional[int] = Field(None, description="사용자 ID로 필터링")
    item_id: Optional[int] = Field(None, description="품목 ID로 필터링")
    category_id: Optional[int] = Field(None, description="카테고리 ID로 필터링")
    status: Optional[RentalStatus] = Field(None, description="상태로 필터링")
    is_overdue: Optional[bool] = Field(None, description="연체 여부로 필터링")
    date_from: Optional[datetime] = Field(None, description="시작 날짜")
    date_to: Optional[datetime] = Field(None, description="종료 날짜")
    due_date_from: Optional[datetime] = Field(None, description="반납 예정일 시작")
    due_date_to: Optional[datetime] = Field(None, description="반납 예정일 종료")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "status": "ACTIVE",
                "is_overdue": False,
                "date_from": "2025-08-29T00:00:00Z",
                "date_to": "2025-08-29T23:59:59Z"
            }
        }


class RentalExtend(BaseModel):
    """대여 연장 스키마 (관리자용)"""
    extend_days: int = Field(..., ge=1, le=7, description="연장할 일수 (1-7일)")
    reason: Optional[str] = Field(None, max_length=500, description="연장 사유")
    
    class Config:
        json_schema_extra = {
            "example": {
                "extend_days": 3,
                "reason": "프로젝트 기간 연장으로 인한 추가 사용 필요"
            }
        }


class RentalHistory(BaseModel):
    """대여 이력 응답 스키마"""
    user_id: int
    user_name: str
    user_student_id: str
    total_rentals: int
    active_rentals: int
    overdue_rentals: int
    completed_rentals: int
    average_rental_days: Optional[float] = Field(None, description="평균 대여 일수")
    last_rental_date: Optional[datetime] = Field(None, description="최근 대여일")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "user_name": "김학생",
                "user_student_id": "202210950",
                "total_rentals": 5,
                "active_rentals": 2,
                "overdue_rentals": 0,
                "completed_rentals": 3,
                "average_rental_days": 4.2,
                "last_rental_date": "2025-08-29T14:00:00Z"
            }
        }