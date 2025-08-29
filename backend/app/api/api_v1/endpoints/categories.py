from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList
from app.services.category_service import CategoryService
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=CategoryList, summary="카테고리 목록 조회")
def get_categories(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    include_inactive: bool = Query(False, description="비활성 카테고리 포함 여부"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    카테고리 목록을 조회합니다.
    
    - **skip**: 건너뛸 개수 (페이지네이션)
    - **limit**: 조회할 개수 (최대 1000개)
    - **include_inactive**: 비활성 카테고리 포함 여부 (관리자만 가능)
    """
    # 일반 사용자는 비활성 카테고리 조회 불가
    if include_inactive and not current_user.is_admin:
        include_inactive = False
    
    try:
        return CategoryService.get_categories(
            db=db, 
            skip=skip, 
            limit=limit, 
            include_inactive=include_inactive
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 목록 조회 중 오류 발생: {str(e)}"
        )


@router.get("/{category_id}", response_model=CategoryResponse, summary="특정 카테고리 조회")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 카테고리의 상세 정보를 조회합니다.
    
    - **category_id**: 조회할 카테고리 ID
    """
    try:
        category = CategoryService.get_category(db=db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        # 일반 사용자는 비활성 카테고리 조회 불가
        if not category.is_active and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        return category
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 조회 중 오류 발생: {str(e)}"
        )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="카테고리 생성")
def create_category(
    category_data: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    새로운 카테고리를 생성합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **name**: 카테고리 이름 (1-100자, 중복 불가)
    - **description**: 카테고리 설명 (최대 500자, 선택사항)
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        return CategoryService.create_category(
            db=db,
            category_data=category_data,
            user_id=current_admin.id,
            ip_address=client_ip
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 생성 중 오류 발생: {str(e)}"
        )


@router.put("/{category_id}", response_model=CategoryResponse, summary="카테고리 수정")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    카테고리 정보를 수정합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **category_id**: 수정할 카테고리 ID
    - **name**: 카테고리 이름 (선택사항)
    - **description**: 카테고리 설명 (선택사항)
    - **is_active**: 활성 상태 (선택사항)
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        category = CategoryService.update_category(
            db=db,
            category_id=category_id,
            category_data=category_data,
            user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 수정 중 오류 발생: {str(e)}"
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="카테고리 삭제")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    카테고리를 삭제합니다 (소프트 삭제).
    
    **관리자 권한이 필요합니다.**
    
    - **category_id**: 삭제할 카테고리 ID
    
    **주의**: 카테고리에 활성 품목이 있는 경우 삭제할 수 없습니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        success = CategoryService.delete_category(
            db=db,
            category_id=category_id,
            user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카테고리를 찾을 수 없습니다"
            )
        
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 삭제 중 오류 발생: {str(e)}"
        )


@router.get("/statistics", response_model=dict, summary="카테고리 통계 조회")
def get_category_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    카테고리 통계 정보를 조회합니다.
    
    **관리자 권한이 필요합니다.**
    
    다음 정보를 포함합니다:
    - 전체/활성 카테고리 개수
    - 카테고리별 품목 개수
    """
    try:
        return CategoryService.get_category_statistics(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"카테고리 통계 조회 중 오류 발생: {str(e)}"
        )