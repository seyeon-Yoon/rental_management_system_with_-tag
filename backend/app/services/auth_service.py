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
            # 세션 쿠키 명시적 관리 및 리디렉션 처리
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                cookies=httpx.Cookies(),
                verify=False  # SSL 검증 비활성화 (대학교 인트라넷 대응)
            ) as client:
                # 상명대학교 SSO 로그인 페이지 접근 (세션 쿠키 및 hidden 필드 획득)
                login_page_response = await client.get(f"{self.base_url}{self.login_endpoint}?ac=Y&ifa=N&id=portal&")
                
                if login_page_response.status_code != 200:
                    logger.error(f"로그인 페이지 접근 실패: {login_page_response.status_code}")
                    return None
                
                # HTML에서 hidden 필드 추출
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(login_page_response.text, 'html.parser')
                
                # 로그인 데이터 준비 (Form 데이터로 전송)
                login_data = {
                    "user_id": student_id,
                    "user_password": password,
                    "user_timezone_offset": "540"  # KST timezone offset
                }
                
                # 실제 페이지에서 발견된 필수 hidden 필드들 추가
                essential_fields = {
                    'ACCESS_TOKEN': '',
                    'OID_KEY': 'SMU', 
                    'SID': 'smu',
                    'USER_ID': '',
                    'l_token': '',  # 매우 중요한 토큰
                    'pwdPolicy': 'N',
                    'user_code': '',
                    'sid': 'portal'
                }
                
                # HTML에서 실제 값 추출하여 업데이트
                for field_name, default_value in essential_fields.items():
                    hidden_input = soup.find('input', {'name': field_name})
                    if hidden_input and hidden_input.get('value'):
                        login_data[field_name] = hidden_input.get('value')
                    else:
                        login_data[field_name] = default_value
                
                # l_token이 비어있으면 다시 시도
                if not login_data.get('l_token'):
                    l_token_input = soup.find('input', {'id': 'l_token'})
                    if l_token_input:
                        login_data['l_token'] = l_token_input.get('value', '')
                        logger.info(f"l_token 추출: {login_data['l_token'][:50]}...") if login_data['l_token'] else None
                
                # Form 전송용 헤더 설정 (실제 브라우저와 동일)
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Origin': self.base_url,
                    'Referer': f"{self.base_url}{self.login_endpoint}?ac=Y&ifa=N&id=portal&",
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # 로그인 요청 (Form 데이터로 전송) - 실제 엔드포인트 사용
                login_response = await client.post(
                    f"{self.base_url}/Login.do",  # 실제 로그인 엔드포인트
                    data=login_data,  # JSON이 아닌 form data
                    headers=headers,
                    follow_redirects=True
                )
                
                # 로그인 성공 여부 확인 (상태 코드 및 응답 내용 확인)
                if login_response.status_code != 200:
                    logger.warning(f"학교 API 로그인 실패 - 상태 코드: {login_response.status_code}")
                    return None
                
                # 디버깅: 실제 응답 내용 로깅 (강제 출력)
                print(f"[DEBUG] 로그인 응답 상태: {login_response.status_code}")
                print(f"[DEBUG] 응답 URL: {login_response.url}")
                print(f"[DEBUG] 응답 내용 (처음 2000자): {login_response.text[:2000]}")
                print(f"[DEBUG] 응답 헤더: {dict(login_response.headers)}")
                
                # 2단계 인증 필요 여부 확인
                if self._check_two_factor_required(login_response.text):
                    logger.warning(f"2단계 인증이 필요합니다: {student_id}")
                    logger.warning("현재 시스템에서는 2단계 인증을 지원하지 않습니다")
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
            
            # 상명대학교 HTML 구조: <li class="major" data-uid="202210950">컴퓨터과학전공</li>
            major_element = soup.find('li', class_='major')
            if not major_element:
                logger.warning("전공 정보를 찾을 수 없습니다")
                logger.debug(f"HTML 내용 (처음 1000자): {html_content[:1000]}")
                return None
            
            student_id = major_element.get('data-uid')
            department = major_element.get_text(strip=True)
            
            # 이름 정보 추출: <li class="name">윤세연님 <span>안녕하세요!</span></li>
            name_element = soup.find('li', class_='name')
            if name_element:
                # "윤세연님"에서 "님" 제거
                name_text = name_element.get_text(strip=True).split()[0]  # "윤세연님 안녕하세요!"에서 첫 번째 단어만
                name = name_text.rstrip('님')  # "님" 제거
            else:
                name = "이름없음"
            
            # 이메일 정보는 이 HTML에서 제공되지 않음
            email = None
            
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
    
    def _check_two_factor_required(self, html_content: str) -> bool:
        """
        2단계 인증 필요 여부 확인
        
        Args:
            html_content: 로그인 후 받은 HTML
            
        Returns:
            True if two-factor authentication is required
        """
        # 2단계 인증 관련 키워드들
        two_factor_indicators = [
            "2단계 인증", "2차 인증", "OTP", "인증번호", 
            "추가 인증", "보안 인증", "휴대폰 인증",
            "two-factor", "verification code", "authenticator",
            "mfa", "multi-factor", "additional verification"
        ]
        
        html_lower = html_content.lower()
        for indicator in two_factor_indicators:
            if indicator.lower() in html_lower:
                return True
        
        # HTML 요소로도 확인
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            # 2단계 인증 관련 폼 요소들 확인
            otp_inputs = soup.find_all('input', {'type': ['text', 'number'], 'name': ['otp', 'code', 'token']})
            if otp_inputs:
                return True
                
            # 2단계 인증 관련 div 클래스 확인
            two_factor_divs = soup.find_all('div', class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['otp', 'mfa', 'two-factor', 'verification']
            ))
            if two_factor_divs:
                return True
                
        except Exception:
            # HTML 파싱 실패해도 키워드 기반 검사는 이미 완료
            pass
        
        return False


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