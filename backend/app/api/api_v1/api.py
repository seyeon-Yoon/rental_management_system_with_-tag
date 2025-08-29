from fastapi import APIRouter

from app.api.api_v1.endpoints import auth

api_router = APIRouter()

# 인증 관련 라우터
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])

# TODO: 추후 다른 엔드포인트들 추가
# api_router.include_router(items.router, prefix="/items", tags=["품목"])
# api_router.include_router(reservations.router, prefix="/reservations", tags=["예약"])
# api_router.include_router(rentals.router, prefix="/rentals", tags=["대여"])
# api_router.include_router(categories.router, prefix="/categories", tags=["카테고리"])
# api_router.include_router(admin.router, prefix="/admin", tags=["관리자"])