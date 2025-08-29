from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Any

from app.db.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, UserResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_active_user, get_auth_service, get_client_ip
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="로그인")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    학교 시스템을 통한 학생 로그인
    
    - **student_id**: 학번
    - **password**: 학교 시스템 비밀번호
    
    성공 시 JWT 토큰과 사용자 정보를 반환합니다.
    """
    client_ip = get_client_ip(request)
    
    try:
        result = await auth_service.login(
            student_id=login_data.student_id,
            password=login_data.password,
            db=db,
            ip_address=client_ip
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다"
        )


@router.post("/logout", response_model=LogoutResponse, summary="로그아웃")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    사용자 로그아웃
    
    현재 사용자의 모든 세션을 종료합니다.
    """
    client_ip = get_client_ip(request)
    
    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("Authorization")
    token = auth_header.replace("Bearer ", "") if auth_header else ""
    
    success = auth_service.logout(
        user_id=current_user.id,
        token=token,
        db=db,
        ip_address=client_ip
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다"
        )
    
    return LogoutResponse()


@router.get("/me", response_model=UserResponse, summary="내 정보 조회")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    현재 로그인한 사용자의 정보 조회
    """
    return UserResponse(
        id=current_user.id,
        student_id=current_user.student_id,
        name=current_user.name,
        department=current_user.department,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active
    )


@router.post("/refresh", response_model=LoginResponse, summary="토큰 갱신")
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """
    JWT 토큰 갱신
    
    기존 토큰이 유효할 때 새로운 토큰을 발급받습니다.
    """
    client_ip = get_client_ip(request)
    
    try:
        # 기존 세션 삭제
        auth_header = request.headers.get("Authorization")
        old_token = auth_header.replace("Bearer ", "") if auth_header else ""
        
        auth_service.logout(
            user_id=current_user.id,
            token=old_token,
            db=db,
            ip_address=client_ip
        )
        
        # 새로운 토큰으로 로그인 (학교 API 호출 없이)
        from app.core.security import create_jwt_token
        
        access_token, session_key = create_jwt_token(current_user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": current_user.id,
                "student_id": current_user.student_id,
                "name": current_user.name,
                "department": current_user.department,
                "email": current_user.email,
                "role": current_user.role.value,
                "is_active": current_user.is_active
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰 갱신 중 오류가 발생했습니다"
        )