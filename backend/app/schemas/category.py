from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """카테고리 기본 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="카테고리 이름")
    description: Optional[str] = Field(None, max_length=500, description="카테고리 설명")


class CategoryCreate(CategoryBase):
    """카테고리 생성 스키마"""
    pass
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "운동용품",
                "description": "축구공, 배구공, 탁구라켓 등 운동에 필요한 용품들"
            }
        }


class CategoryUpdate(BaseModel):
    """카테고리 업데이트 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="카테고리 이름")
    description: Optional[str] = Field(None, max_length=500, description="카테고리 설명")
    is_active: Optional[bool] = Field(None, description="활성 상태")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "전자기기",
                "description": "보조배터리, 계산기 등 전자제품",
                "is_active": True
            }
        }


class CategoryResponse(CategoryBase):
    """카테고리 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    active_items_count: Optional[int] = Field(None, description="활성 품목 개수")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "운동용품",
                "description": "축구공, 배구공, 탁구라켓 등 운동에 필요한 용품들",
                "is_active": True,
                "created_at": "2025-08-29T10:30:00Z",
                "updated_at": "2025-08-29T10:30:00Z",
                "active_items_count": 15
            }
        }


class CategoryList(BaseModel):
    """카테고리 목록 응답 스키마"""
    categories: list[CategoryResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {
                        "id": 1,
                        "name": "운동용품",
                        "description": "축구공, 배구공 등",
                        "is_active": True,
                        "created_at": "2025-08-29T10:30:00Z",
                        "updated_at": "2025-08-29T10:30:00Z",
                        "active_items_count": 15
                    }
                ],
                "total": 8
            }
        }