from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse, ItemList, ItemFilter, ItemStatus
from app.services.item_service import ItemService
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=ItemList, summary="품목 목록 조회")
def get_items(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    status: Optional[ItemStatus] = Query(None, description="상태 필터"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터 (관리자만)"),
    search: Optional[str] = Query(None, min_length=1, max_length=100, description="검색어"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    품목 목록을 조회합니다.
    
    - **skip**: 건너뛸 개수 (페이지네이션)
    - **limit**: 조회할 개수 (최대 1000개)
    - **category_id**: 특정 카테고리의 품목만 조회
    - **status**: 특정 상태의 품목만 조회
    - **is_active**: 활성 상태 필터 (관리자만 사용 가능)
    - **search**: 품목명, 설명, 일련번호로 검색
    """
    # 일반 사용자는 비활성 품목 조회 불가
    if is_active is not None and not current_user.is_admin:
        is_active = True  # 강제로 활성 품목만 조회
    
    try:
        filters = ItemFilter(
            category_id=category_id,
            status=status,
            is_active=is_active,
            search=search
        )
        
        return ItemService.get_items(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"품목 목록 조회 중 오류 발생: {str(e)}"
        )


@router.get("/available", response_model=list[ItemResponse], summary="대여 가능한 품목 조회")
def get_available_items(
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    현재 대여 가능한 품목 목록을 조회합니다.
    
    - **category_id**: 특정 카테고리의 품목만 조회
    - **skip**: 건너뛸 개수
    - **limit**: 조회할 개수
    """
    try:
        return ItemService.get_available_items(
            db=db,
            category_id=category_id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 가능한 품목 조회 중 오류 발생: {str(e)}"
        )


@router.get("/{item_id}", response_model=ItemResponse, summary="특정 품목 조회")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 품목의 상세 정보를 조회합니다.
    
    - **item_id**: 조회할 품목 ID
    """
    try:
        item = ItemService.get_item(db=db, item_id=item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
            )
        
        # 일반 사용자는 비활성 품목 조회 불가
        if not item.is_active and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"품목 조회 중 오류 발생: {str(e)}"
        )


@router.get("/serial/{serial_number}", response_model=ItemResponse, summary="일련번호로 품목 조회")
def get_item_by_serial(
    serial_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    일련번호로 품목을 조회합니다.
    
    - **serial_number**: 품목 일련번호
    """
    try:
        item = ItemService.get_item_by_serial(db=db, serial_number=serial_number)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
            )
        
        # 일반 사용자는 비활성 품목 조회 불가
        if not item.is_active and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"품목 조회 중 오류 발생: {str(e)}"
        )


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="품목 생성")
def create_item(
    item_data: ItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    새로운 품목을 생성합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **name**: 품목명 (1-100자)
    - **description**: 품목 설명 (최대 500자, 선택사항)
    - **serial_number**: 일련번호 (1-50자, 중복 불가)
    - **category_id**: 카테고리 ID
    - **item_metadata**: 추가 메타데이터 (선택사항)
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        return ItemService.create_item(
            db=db,
            item_data=item_data,
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
            detail=f"품목 생성 중 오류 발생: {str(e)}"
        )


@router.put("/{item_id}", response_model=ItemResponse, summary="품목 수정")
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    품목 정보를 수정합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **item_id**: 수정할 품목 ID
    - **name**: 품목명 (선택사항)
    - **description**: 품목 설명 (선택사항)
    - **status**: 품목 상태 (선택사항)
    - **category_id**: 카테고리 ID (선택사항)
    - **item_metadata**: 메타데이터 (선택사항)
    - **is_active**: 활성 상태 (선택사항)
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        item = ItemService.update_item(
            db=db,
            item_id=item_id,
            item_data=item_data,
            user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
            )
        
        return item
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
            detail=f"품목 수정 중 오류 발생: {str(e)}"
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="품목 삭제")
def delete_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    품목을 삭제합니다 (소프트 삭제).
    
    **관리자 권한이 필요합니다.**
    
    - **item_id**: 삭제할 품목 ID
    
    **주의**: 대여중이거나 예약된 품목은 삭제할 수 없습니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        success = ItemService.delete_item(
            db=db,
            item_id=item_id,
            user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="품목을 찾을 수 없습니다"
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
            detail=f"품목 삭제 중 오류 발생: {str(e)}"
        )


@router.get("/statistics", response_model=dict, summary="품목 통계 조회")
def get_item_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    품목 통계 정보를 조회합니다.
    
    **관리자 권한이 필요합니다.**
    
    다음 정보를 포함합니다:
    - 전체 품목 개수
    - 상태별 품목 개수
    - 카테고리별 품목 개수
    """
    try:
        return ItemService.get_item_statistics(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"품목 통계 조회 중 오류 발생: {str(e)}"
        )