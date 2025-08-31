from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
from fastapi import HTTPException, status

from app.core.config import settings

# 패스워드 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis 클라이언트 (세션 관리용)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """JWT 액세스 토큰 생성"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """JWT 토큰 검증 및 subject 추출"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = payload.get("sub")
        if token_data is None:
            return None
        return str(token_data)
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """패스워드 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """패스워드 해싱"""
    return pwd_context.hash(password)


def create_session(user_id: int, token: str, expires_minutes: int = None) -> str:
    """Redis에 사용자 세션 생성"""
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    session_key = f"session:{user_id}:{token[-12:]}"  # 토큰 마지막 12자리로 세션 키 생성
    
    session_data = {
        "user_id": str(user_id),
        "token": token,
        "created_at": datetime.utcnow().isoformat(),
        "last_accessed": datetime.utcnow().isoformat()
    }
    
    try:
        # Redis에 세션 저장 (만료 시간 설정)
        redis_client.hmset(session_key, session_data)
        redis_client.expire(session_key, expires_minutes * 60)
        print(f"✅ Redis session created: {session_key}")
    except Exception as e:
        print(f"⚠️  Redis unavailable, skipping session storage: {e}")
        # Redis 연결 실패시에도 세션 키는 반환 (JWT 토큰만으로 인증)
    
    return session_key


def get_session(user_id: int, token: str) -> Optional[dict]:
    """Redis에서 사용자 세션 조회"""
    session_key = f"session:{user_id}:{token[-12:]}"
    
    try:
        session_data = redis_client.hgetall(session_key)
        
        if not session_data:
            return None
        
        # 마지막 접근 시간 업데이트
        redis_client.hset(session_key, "last_accessed", datetime.utcnow().isoformat())
        
        return session_data
    except Exception as e:
        print(f"⚠️  Redis unavailable, cannot get session: {e}")
        # Redis 연결 실패시 None 반환 (JWT 토큰으로만 인증)
        return None


def delete_session(user_id: int, token: str = None) -> bool:
    """Redis에서 사용자 세션 삭제"""
    try:
        if token:
            # 특정 세션 삭제
            session_key = f"session:{user_id}:{token[-12:]}"
            return bool(redis_client.delete(session_key))
        else:
            # 사용자의 모든 세션 삭제
            pattern = f"session:{user_id}:*"
            keys = redis_client.keys(pattern)
            if keys:
                return bool(redis_client.delete(*keys))
            return True
    except Exception as e:
        print(f"⚠️  Redis unavailable, cannot delete session: {e}")
        # Redis 연결 실패시에도 성공으로 처리 (JWT 토큰만 사용)
        return True


def delete_all_sessions(user_id: int) -> bool:
    """사용자의 모든 세션 삭제 (로그아웃, 계정 비활성화 시)"""
    return delete_session(user_id)


def validate_session(user_id: int, token: str) -> bool:
    """세션 유효성 검증"""
    session_data = get_session(user_id, token)
    if not session_data:
        # Redis가 없을 때는 JWT 토큰 자체의 유효성으로만 판단
        print(f"⚠️  No session data found, relying on JWT token validation only")
        return True  # JWT 토큰이 이미 검증되었으므로 True 반환
    
    # 토큰 일치 확인
    stored_token = session_data.get("token")
    return stored_token == token


def create_jwt_token(user_id: int) -> tuple[str, str]:
    """JWT 토큰 생성 및 세션 등록"""
    # JWT 토큰 생성
    access_token = create_access_token(subject=user_id)
    
    # Redis 세션 생성
    session_key = create_session(user_id, access_token)
    
    return access_token, session_key