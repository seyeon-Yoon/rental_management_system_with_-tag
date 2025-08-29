from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.schemas.rental import (
    RentalCreate, RentalUpdate, RentalResponse, RentalList, 
    RentalFilter, RentalStatus, RentalReturn, RentalExtend, RentalHistory
)
from app.services.rental_service import RentalService
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=RentalList, summary="대여 목록 조회")
def get_rentals(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_id: Optional[int] = Query(None, description="사용자 ID 필터 (관리자만)"),
    item_id: Optional[int] = Query(None, description="품목 ID 필터"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    status: Optional[RentalStatus] = Query(None, description="상태 필터"),
    is_overdue: Optional[bool] = Query(None, description="연체 여부 필터"),
    date_from: Optional[datetime] = Query(None, description="시작 날짜"),
    date_to: Optional[datetime] = Query(None, description="종료 날짜"),
    due_date_from: Optional[datetime] = Query(None, description="반납 예정일 시작"),
    due_date_to: Optional[datetime] = Query(None, description="반납 예정일 종료"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    대여 목록을 조회합니다.
    
    - **skip**: 건너뛸 개수 (페이지네이션)
    - **limit**: 조회할 개수 (최대 1000개)
    - **user_id**: 특정 사용자의 대여만 조회 (관리자만 사용 가능)
    - **item_id**: 특정 품목의 대여만 조회
    - **category_id**: 특정 카테고리의 대여만 조회
    - **status**: 특정 상태의 대여만 조회
    - **is_overdue**: 연체된 대여만 조회
    - **date_from, date_to**: 대여 날짜 범위 필터
    - **due_date_from, due_date_to**: 반납 예정일 범위 필터
    
    **일반 사용자는 자신의 대여만 조회 가능합니다.**
    """
    try:
        filters = RentalFilter(
            user_id=user_id,
            item_id=item_id,
            category_id=category_id,
            status=status,
            is_overdue=is_overdue,
            date_from=date_from,
            date_to=date_to,
            due_date_from=due_date_from,
            due_date_to=due_date_to
        )
        
        return RentalService.get_rentals(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 목록 조회 중 오류 발생: {str(e)}"
        )


@router.get("/my", response_model=list[RentalResponse], summary="내 활성 대여 조회")
def get_my_active_rentals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    현재 사용자의 활성 대여 목록을 조회합니다.
    
    활성 대여: ACTIVE 또는 OVERDUE 상태의 대여들
    """
    try:
        return RentalService.get_user_active_rentals(
            db=db,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 대여 조회 중 오류 발생: {str(e)}"
        )


@router.get("/{rental_id}", response_model=RentalResponse, summary="특정 대여 조회")
def get_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 대여의 상세 정보를 조회합니다.
    
    - **rental_id**: 조회할 대여 ID
    
    **일반 사용자는 자신의 대여만 조회 가능합니다.**
    """
    try:
        rental = RentalService.get_rental(
            db=db,
            rental_id=rental_id,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대여를 찾을 수 없습니다"
            )
        
        return rental
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 조회 중 오류 발생: {str(e)}"
        )


@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED, summary="대여 생성")
def create_rental(
    rental_data: RentalCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    새로운 대여를 생성합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **item_id**: 대여할 품목 ID
    - **reservation_id**: 연결된 예약 ID (선택사항)
    - **notes**: 대여 메모 (선택사항)
    
    **일반적으로 예약 확인 시 자동으로 생성되지만, 수동 생성도 가능합니다.**
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        # user_id를 요청에서 받아야 하는데, 현재 스키마에 없으므로 예외 처리
        # 실제로는 예약 확인 시에만 대여가 생성되므로, 이 엔드포인트는 관리자용 특수 케이스
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="대여는 예약 수령 확인을 통해 자동 생성됩니다. /reservations/{id}/confirm을 사용하세요."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 생성 중 오류 발생: {str(e)}"
        )


@router.post("/{rental_id}/return", response_model=RentalResponse, summary="대여 반납")
def return_rental(
    rental_id: int,
    return_data: RentalReturn,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    대여를 반납 처리합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **rental_id**: 반납할 대여 ID
    - **admin_notes**: 반납 확인 메모 (선택사항)
    - **condition_notes**: 품목 상태 메모 (선택사항)
    
    반납 처리 후 품목은 AVAILABLE 상태로 변경됩니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        rental = RentalService.return_rental(
            db=db,
            rental_id=rental_id,
            return_data=return_data,
            admin_user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대여를 찾을 수 없습니다"
            )
        
        return rental
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
            detail=f"대여 반납 중 오류 발생: {str(e)}"
        )


@router.post("/{rental_id}/extend", response_model=RentalResponse, summary="대여 연장")
def extend_rental(
    rental_id: int,
    extend_data: RentalExtend,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    대여를 연장 처리합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **rental_id**: 연장할 대여 ID
    - **extend_days**: 연장할 일수 (1-7일)
    - **reason**: 연장 사유 (선택사항)
    
    연체 상태였던 대여도 연장 시 ACTIVE 상태로 복원됩니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        rental = RentalService.extend_rental(
            db=db,
            rental_id=rental_id,
            extend_data=extend_data,
            admin_user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대여를 찾을 수 없습니다"
            )
        
        return rental
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
            detail=f"대여 연장 중 오류 발생: {str(e)}"
        )


@router.post("/overdue", response_model=dict, summary="연체된 대여 일괄 처리")
def mark_overdue_rentals(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    연체된 대여들을 일괄 처리합니다.
    
    **관리자 권한이 필요합니다.**
    
    반납 예정일을 초과한 ACTIVE 상태의 대여들을 OVERDUE 상태로 변경합니다.
    
    **일반적으로 스케줄러에 의해 자동 실행되지만, 수동 실행도 가능합니다.**
    """
    try:
        overdue_count = RentalService.mark_overdue_rentals(db=db)
        
        return {
            "message": f"{overdue_count}개의 대여가 연체 처리되었습니다",
            "overdue_count": overdue_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연체 처리 중 오류 발생: {str(e)}"
        )


@router.get("/history", response_model=list[RentalHistory], summary="대여 이력 조회")
def get_rental_history(
    user_id: Optional[int] = Query(None, description="특정 사용자 ID"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    대여 이력 통계를 조회합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **user_id**: 특정 사용자의 이력만 조회 (선택사항)
    - **skip, limit**: 페이지네이션
    
    사용자별 대여 통계 정보를 제공합니다:
    - 총 대여 횟수, 현재 활성/연체/완료 대여 수
    - 평균 대여 기간, 최근 대여일
    """
    try:
        return RentalService.get_rental_history(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 이력 조회 중 오류 발생: {str(e)}"
        )


@router.get("/statistics", response_model=dict, summary="대여 통계 조회")
def get_rental_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    대여 통계 정보를 조회합니다.
    
    **관리자 권한이 필요합니다.**
    
    다음 정보를 포함합니다:
    - 전체 대여 개수
    - 상태별 대여 개수
    - 오늘 대여 개수
    - 현재 활성/연체 대여 개수
    - 평균 대여 기간
    """
    try:
        return RentalService.get_rental_statistics(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대여 통계 조회 중 오류 발생: {str(e)}"
        )