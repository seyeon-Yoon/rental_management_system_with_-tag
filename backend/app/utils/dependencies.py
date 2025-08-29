from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """AuthService 인스턴스 제공"""
    return AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """현재 인증된 사용자 조회"""
    token = credentials.credentials
    user = auth_service.get_current_user(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 유효하지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """현재 활성 사용자 조회"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성 사용자입니다"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """현재 관리자 사용자 조회"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """선택적 사용자 인증 (토큰이 없어도 에러 발생하지 않음)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    return auth_service.get_current_user(token, db)


def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    # X-Forwarded-For 헤더 확인 (프록시 뒤에 있을 때)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 첫 번째 IP가 실제 클라이언트 IP
        return forwarded_for.split(",")[0].strip()
    
    # X-Real-IP 헤더 확인 (Nginx 등)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 직접 연결된 경우
    return request.client.host if request.client else "unknown"


class RequirePermissions:
    """권한 기반 데코레이터 클래스"""
    
    def __init__(self, *required_roles: UserRole):
        self.required_roles = required_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """필요한 권한 확인"""
        if self.required_roles and current_user.role not in self.required_roles:
            role_names = [role.value for role in self.required_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"다음 권한 중 하나가 필요합니다: {', '.join(role_names)}"
            )
        return current_user


# 편의성 함수들
require_admin = RequirePermissions(UserRole.ADMIN)
require_student_or_admin = RequirePermissions(UserRole.STUDENT, UserRole.ADMIN)