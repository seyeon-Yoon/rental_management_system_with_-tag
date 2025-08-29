from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.schemas.reservation import (
    ReservationCreate, ReservationUpdate, ReservationResponse, 
    ReservationList, ReservationFilter, ReservationStatus,
    ReservationConfirm, ReservationCancel
)
from app.services.reservation_service import ReservationService
from app.api.deps import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get("", response_model=ReservationList, summary="예약 목록 조회")
def get_reservations(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    user_id: Optional[int] = Query(None, description="사용자 ID 필터 (관리자만)"),
    item_id: Optional[int] = Query(None, description="품목 ID 필터"),
    category_id: Optional[int] = Query(None, description="카테고리 ID 필터"),
    status: Optional[ReservationStatus] = Query(None, description="상태 필터"),
    is_expired: Optional[bool] = Query(None, description="만료 여부 필터"),
    date_from: Optional[datetime] = Query(None, description="시작 날짜"),
    date_to: Optional[datetime] = Query(None, description="종료 날짜"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    예약 목록을 조회합니다.
    
    - **skip**: 건너뛸 개수 (페이지네이션)
    - **limit**: 조회할 개수 (최대 1000개)
    - **user_id**: 특정 사용자의 예약만 조회 (관리자만 사용 가능)
    - **item_id**: 특정 품목의 예약만 조회
    - **category_id**: 특정 카테고리의 예약만 조회
    - **status**: 특정 상태의 예약만 조회
    - **is_expired**: 만료된 예약만 조회
    - **date_from, date_to**: 날짜 범위 필터
    
    **일반 사용자는 자신의 예약만 조회 가능합니다.**
    """
    try:
        filters = ReservationFilter(
            user_id=user_id,
            item_id=item_id,
            category_id=category_id,
            status=status,
            is_expired=is_expired,
            date_from=date_from,
            date_to=date_to
        )
        
        return ReservationService.get_reservations(
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
            detail=f"예약 목록 조회 중 오류 발생: {str(e)}"
        )


@router.get("/my", response_model=list[ReservationResponse], summary="내 활성 예약 조회")
def get_my_active_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    현재 사용자의 활성 예약 목록을 조회합니다.
    
    활성 예약: PENDING 상태이면서 만료되지 않은 예약들
    """
    try:
        return ReservationService.get_user_active_reservations(
            db=db,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 예약 조회 중 오류 발생: {str(e)}"
        )


@router.get("/{reservation_id}", response_model=ReservationResponse, summary="특정 예약 조회")
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 예약의 상세 정보를 조회합니다.
    
    - **reservation_id**: 조회할 예약 ID
    
    **일반 사용자는 자신의 예약만 조회 가능합니다.**
    """
    try:
        reservation = ReservationService.get_reservation(
            db=db,
            reservation_id=reservation_id,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="예약을 찾을 수 없습니다"
            )
        
        return reservation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예약 조회 중 오류 발생: {str(e)}"
        )


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED, summary="예약 생성")
def create_reservation(
    reservation_data: ReservationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    새로운 예약을 생성합니다.
    
    - **item_id**: 예약할 품목 ID
    - **notes**: 예약 메모 (선택사항)
    
    **예약 규칙:**
    - 품목이 AVAILABLE 상태여야 함
    - 같은 품목에 대한 중복 예약 불가
    - 예약 후 1시간 내 수령 필요
    - 1시간 초과 시 자동 취소
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        return ReservationService.create_reservation(
            db=db,
            reservation_data=reservation_data,
            user_id=current_user.id,
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
            detail=f"예약 생성 중 오류 발생: {str(e)}"
        )


@router.post("/{reservation_id}/confirm", response_model=ReservationResponse, summary="예약 수령 확인")
def confirm_reservation(
    reservation_id: int,
    confirm_data: ReservationConfirm,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    예약을 수령 확인 처리합니다.
    
    **관리자 권한이 필요합니다.**
    
    - **reservation_id**: 확인할 예약 ID
    - **admin_notes**: 수령 확인 메모 (선택사항)
    
    수령 확인 후 품목은 RENTED 상태로 변경됩니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        reservation = ReservationService.confirm_reservation(
            db=db,
            reservation_id=reservation_id,
            confirm_data=confirm_data,
            admin_user_id=current_admin.id,
            ip_address=client_ip
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="예약을 찾을 수 없습니다"
            )
        
        return reservation
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
            detail=f"예약 확인 중 오류 발생: {str(e)}"
        )


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse, summary="예약 취소")
def cancel_reservation(
    reservation_id: int,
    cancel_data: ReservationCancel,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    예약을 취소합니다.
    
    - **reservation_id**: 취소할 예약 ID
    - **reason**: 취소 사유 (선택사항)
    
    **일반 사용자는 자신의 예약만 취소 가능합니다.**
    **관리자는 모든 예약을 취소할 수 있습니다.**
    
    취소 후 품목은 AVAILABLE 상태로 복원됩니다.
    """
    try:
        # 클라이언트 IP 주소 추출
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        reservation = ReservationService.cancel_reservation(
            db=db,
            reservation_id=reservation_id,
            cancel_data=cancel_data,
            user_id=current_user.id,
            is_admin=current_user.is_admin,
            ip_address=client_ip
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="예약을 찾을 수 없습니다"
            )
        
        return reservation
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
            detail=f"예약 취소 중 오류 발생: {str(e)}"
        )


@router.post("/expire", response_model=dict, summary="만료된 예약 일괄 처리")
def expire_reservations(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    만료된 예약들을 일괄 처리합니다.
    
    **관리자 권한이 필요합니다.**
    
    1시간을 초과한 PENDING 상태의 예약들을 EXPIRED 상태로 변경하고
    해당 품목들을 AVAILABLE 상태로 복원합니다.
    
    **일반적으로 스케줄러에 의해 자동 실행되지만, 수동 실행도 가능합니다.**
    """
    try:
        expired_count = ReservationService.expire_reservations(db=db)
        
        return {
            "message": f"{expired_count}개의 예약이 만료 처리되었습니다",
            "expired_count": expired_count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예약 만료 처리 중 오류 발생: {str(e)}"
        )


@router.get("/statistics", response_model=dict, summary="예약 통계 조회")
def get_reservation_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    예약 통계 정보를 조회합니다.
    
    **관리자 권한이 필요합니다.**
    
    다음 정보를 포함합니다:
    - 전체 예약 개수
    - 상태별 예약 개수
    - 오늘 예약 개수
    - 현재 활성 예약 개수
    """
    try:
        return ReservationService.get_reservation_statistics(db=db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예약 통계 조회 중 오류 발생: {str(e)}"
        )