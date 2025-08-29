from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    """품목 상태"""
    AVAILABLE = "AVAILABLE"  # 대여 가능
    RESERVED = "RESERVED"    # 예약됨
    RENTED = "RENTED"        # 대여중
    MAINTENANCE = "MAINTENANCE"  # 정비중


class ItemBase(BaseModel):
    """품목 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="품목명")
    description: Optional[str] = Field(None, max_length=500, description="품목 설명")
    serial_number: str = Field(..., min_length=1, max_length=50, description="일련번호 (고유 식별자)")
    category_id: int = Field(..., description="카테고리 ID")
    item_metadata: Optional[dict] = Field(None, description="추가 메타데이터 (JSONB)")


class ItemCreate(ItemBase):
    """품목 생성 스키마"""
    pass
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "보조배터리",
                "description": "20000mAh 대용량 보조배터리",
                "serial_number": "PWR001",
                "category_id": 2,
                "item_metadata": {
                    "capacity": "20000mAh",
                    "brand": "Samsung",
                    "model": "EB-P3300"
                }
            }
        }


class ItemUpdate(BaseModel):
    """품목 업데이트 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="품목명")
    description: Optional[str] = Field(None, max_length=500, description="품목 설명")
    status: Optional[ItemStatus] = Field(None, description="품목 상태")
    category_id: Optional[int] = Field(None, description="카테고리 ID")
    item_metadata: Optional[dict] = Field(None, description="추가 메타데이터")
    is_active: Optional[bool] = Field(None, description="활성 상태")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "보조배터리 (수정됨)",
                "description": "25000mAh 초고용량 보조배터리",
                "status": "MAINTENANCE",
                "item_metadata": {
                    "capacity": "25000mAh",
                    "brand": "Samsung",
                    "model": "EB-P4300",
                    "last_maintenance": "2025-08-29"
                },
                "is_active": True
            }
        }


class ItemResponse(ItemBase):
    """품목 응답 스키마"""
    id: int
    status: ItemStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = Field(None, description="카테고리명")
    current_rental_id: Optional[int] = Field(None, description="현재 대여 ID (대여중인 경우)")
    current_reservation_id: Optional[int] = Field(None, description="현재 예약 ID (예약됨인 경우)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "보조배터리",
                "description": "20000mAh 대용량 보조배터리",
                "serial_number": "PWR001",
                "category_id": 2,
                "category_name": "전자기기",
                "status": "AVAILABLE",
                "is_active": True,
                "created_at": "2025-08-29T10:30:00Z",
                "updated_at": "2025-08-29T10:30:00Z",
                "item_metadata": {
                    "capacity": "20000mAh",
                    "brand": "Samsung",
                    "model": "EB-P3300"
                },
                "current_rental_id": None,
                "current_reservation_id": None
            }
        }


class ItemList(BaseModel):
    """품목 목록 응답 스키마"""
    items: list[ItemResponse]
    total: int
    available_count: int
    rented_count: int
    reserved_count: int
    maintenance_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "보조배터리",
                        "description": "20000mAh 대용량",
                        "serial_number": "PWR001",
                        "category_id": 2,
                        "category_name": "전자기기",
                        "status": "AVAILABLE",
                        "is_active": True,
                        "created_at": "2025-08-29T10:30:00Z",
                        "updated_at": "2025-08-29T10:30:00Z",
                        "item_metadata": {"capacity": "20000mAh"},
                        "current_rental_id": None,
                        "current_reservation_id": None
                    }
                ],
                "total": 45,
                "available_count": 38,
                "rented_count": 5,
                "reserved_count": 2,
                "maintenance_count": 0
            }
        }


class ItemFilter(BaseModel):
    """품목 필터 스키마"""
    category_id: Optional[int] = Field(None, description="카테고리 ID로 필터링")
    status: Optional[ItemStatus] = Field(None, description="상태로 필터링")
    is_active: Optional[bool] = Field(None, description="활성 상태로 필터링")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="품목명 검색")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 2,
                "status": "AVAILABLE",
                "is_active": True,
                "search": "보조배터리"
            }
        }