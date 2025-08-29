import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.core.config import settings
from app.core.security import create_jwt_token, verify_token, validate_session, delete_all_sessions
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.db.database import get_db

logger = logging.getLogger(__name__)


class UniversityAPIService:
    """대학교 API 연동 서비스"""
    
    def __init__(self):
        self.base_url = settings.UNIVERSITY_API_BASE_URL
        self.login_endpoint = settings.UNIVERSITY_API_LOGIN_ENDPOINT
        self.timeout = settings.UNIVERSITY_API_TIMEOUT
    
    async def authenticate_student(self, student_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        대학교 시스템으로 학생 인증
        
        Args:
            student_id: 학번
            password: 비밀번호
            
        Returns:
            Dict containing user info if successful, None if failed
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 로그인 페이지 접근 (세션 쿠키 획득)
                login_page_response = await client.get(f"{self.base_url}/login")
                
                # 로그인 데이터 준비
                login_data = {
                    "student_id": student_id,
                    "password": password
                }
                
                # 로그인 요청
                login_response = await client.post(
                    f"{self.base_url}{self.login_endpoint}",
                    data=login_data,
                    follow_redirects=True
                )
                
                # 로그인 성공 여부 확인 (상태 코드 및 응답 내용 확인)
                if login_response.status_code != 200:
                    logger.warning(f"학교 API 로그인 실패 - 상태 코드: {login_response.status_code}")
                    return None
                
                # HTML 파싱하여 사용자 정보 추출
                user_info = self._parse_user_info(login_response.text)
                
                if user_info and user_info.get("student_id") == student_id:
                    logger.info(f"대학교 API 인증 성공: {student_id}")
                    return user_info
                else:
                    logger.warning(f"대학교 API 인증 실패: {student_id}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"대학교 API 타임아웃: {student_id}")
            return None
        except Exception as e:
            logger.error(f"대학교 API 연동 오류: {e}")
            return None
    
    def _parse_user_info(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        HTML에서 사용자 정보 파싱
        
        Args:
            html_content: 로그인 후 받은 HTML
            
        Returns:
            Dict containing parsed user info
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 예시: <li class="major" data-uid="202210950">컴퓨터과학전공</li>
            major_element = soup.find('li', class_='major')
            if not major_element:
                logger.warning("전공 정보를 찾을 수 없습니다")
                return None
            
            student_id = major_element.get('data-uid')
            department = major_element.get_text(strip=True)
            
            # 이름 정보 추출 (HTML 구조에 따라 조정 필요)
            name_element = soup.find('span', class_='username') or soup.find('span', class_='name')
            name = name_element.get_text(strip=True) if name_element else "이름없음"
            
            # 이메일 정보 추출 (선택사항)
            email_element = soup.find('span', class_='email')
            email = email_element.get_text(strip=True) if email_element else None
            
            # 융공대 학생 여부 확인
            is_convergence_engineering_student = self._is_convergence_engineering_department(department)
            
            if not is_convergence_engineering_student:
                logger.warning(f"융공대 학생이 아닙니다: {department}")
                return None
            
            return {
                "student_id": student_id,
                "name": name,
                "department": department,
                "email": email
            }
            
        except Exception as e:
            logger.error(f"HTML 파싱 오류: {e}")
            return None
    
    def _is_convergence_engineering_department(self, department: str) -> bool:
        """융합공과대학 소속 여부 확인"""
        if not department:
            return False
        
        # 융공대 전공 리스트에서 확인
        return department in settings.CONVERGENCE_ENGINEERING_MAJORS


class AuthService:
    """인증 서비스"""
    
    def __init__(self):
        self.university_api = UniversityAPIService()
    
    async def login(self, student_id: str, password: str, db: Session, ip_address: str = None) -> Dict[str, Any]:
        """
        로그인 처리
        
        Args:
            student_id: 학번
            password: 비밀번호
            db: 데이터베이스 세션
            ip_address: 클라이언트 IP
            
        Returns:
            Dict containing token and user info
            
        Raises:
            ValueError: 인증 실패 시
        """
        # 대학교 API로 인증
        university_user_info = await self.university_api.authenticate_student(student_id, password)
        if not university_user_info:
            # 감사 로그 기록
            audit_log = AuditLog.create_log(
                action="LOGIN_FAILED",
                table_name="users",
                description=f"로그인 실패: {student_id}",
                ip_address=ip_address
            )
            db.add(audit_log)
            db.commit()
            
            raise ValueError("학번 또는 비밀번호가 잘못되었습니다")
        
        # 데이터베이스에서 사용자 조회 또는 생성
        user = db.query(User).filter(User.student_id == student_id).first()
        
        if not user:
            # 신규 사용자 생성
            user = User(
                student_id=university_user_info["student_id"],
                name=university_user_info["name"],
                department=university_user_info["department"],
                email=university_user_info.get("email"),
                role=UserRole.STUDENT
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # 감사 로그 기록
            audit_log = AuditLog.create_log(
                action="USER_CREATED",
                table_name="users",
                user_id=user.id,
                record_id=user.id,
                description=f"신규 사용자 생성: {student_id}",
                ip_address=ip_address
            )
            db.add(audit_log)
            
        else:
            # 기존 사용자 정보 업데이트
            user.name = university_user_info["name"]
            user.department = university_user_info["department"]
            if university_user_info.get("email"):
                user.email = university_user_info["email"]
            user.last_login_at = datetime.utcnow()
        
        # 비활성 사용자 체크
        if not user.is_active:
            raise ValueError("비활성화된 계정입니다")
        
        # JWT 토큰 및 세션 생성
        access_token, session_key = create_jwt_token(user.id)
        
        # 감사 로그 기록
        audit_log = AuditLog.create_log(
            action="LOGIN_SUCCESS",
            table_name="users",
            user_id=user.id,
            record_id=user.id,
            description=f"로그인 성공: {student_id}",
            ip_address=ip_address
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "student_id": user.student_id,
                "name": user.name,
                "department": user.department,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active
            }
        }
    
    def logout(self, user_id: int, token: str, db: Session, ip_address: str = None) -> bool:
        """
        로그아웃 처리
        
        Args:
            user_id: 사용자 ID
            token: JWT 토큰
            db: 데이터베이스 세션
            ip_address: 클라이언트 IP
            
        Returns:
            True if successful
        """
        # 세션 삭제
        success = delete_all_sessions(user_id)
        
        if success:
            # 감사 로그 기록
            audit_log = AuditLog.create_log(
                action="LOGOUT",
                table_name="users",
                user_id=user_id,
                record_id=user_id,
                description="로그아웃",
                ip_address=ip_address
            )
            db.add(audit_log)
            db.commit()
        
        return success
    
    def get_current_user(self, token: str, db: Session) -> Optional[User]:
        """
        현재 사용자 조회
        
        Args:
            token: JWT 토큰
            db: 데이터베이스 세션
            
        Returns:
            User object if valid, None if invalid
        """
        # JWT 토큰 검증
        user_id_str = verify_token(token)
        if not user_id_str:
            return None
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            return None
        
        # 세션 유효성 검증
        if not validate_session(user_id, token):
            return None
        
        # 사용자 조회
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        return user