# API 의존성 함수들을 utils.dependencies에서 가져와서 재사용
from app.utils.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    get_optional_current_user,
    get_client_ip,
    RequirePermissions,
    require_admin,
    require_student_or_admin,
    get_auth_service
)