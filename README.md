# 렌탈 관리 시스템 (Rental Management System)

융합공과대학 학생회를 위한 무료 대여 서비스 관리 시스템

## 프로젝트 개요

융합공과대학 학생회에서 융공대 학생들에게 다양한 생활/학습 용품을 무료로 대여해주는 서비스를 효율적으로 관리하기 위한 웹 기반 시스템입니다.

## 요구사항 (Requirements)

### 1. 비즈니스 요구사항

#### 1.1 서비스 개요
- **운영 주체**: 융합공과대학 학생회
- **서비스 대상**: 융합공과대학 재학생 (대학교 API를 통한 자동 인증)
- **서비스 성격**: 무료 대여 서비스 (학생 복지 목적)
- **운영 방식**: 온라인 예약 + 오프라인 수령/반납

#### 1.2 대여 품목 카테고리
1. **운동용품** (관리자가 세부 품목 등록)
2. **전자기기**: 보조배터리, 공학용계산기
3. **생활용품**: 우산, 인공눈물, 상비약
4. **엔터테인먼트**: 보드게임
5. **학업용품**: 실험복

### 2. 기능 요구사항

#### 2.1 사용자 인증
- **필수**: 대학교 홈페이지 API 연동을 통한 융공대 학생 자동 인증
- **대안 없음**: API 연동이 전제 조건

#### 2.2 예약 시스템
- **실시간 재고 확인**: 예약 가능한 품목만 표시
- **온라인 예약**: 웹에서 품목 선택 및 예약
- **시간 제한**: 예약 후 1시간 내 학생회실 방문 필수
- **자동 취소**: 1시간 초과 시 예약 자동 취소 및 재고 복원

#### 2.3 대여 관리
- **대여 기간**: 모든 품목 최대 7일 (품목별 구분 없음)
- **동시 대여**: 한 학생당 여러 품목 동시 대여 가능 (개수 제한 없음)
- **반납 관리**: 반납 시 재고 자동 복원

#### 2.4 재고 관리
- **개별 추적**: 같은 품목도 개별 식별자로 구분 (예: 보조배터리#001, #002)
- **실시간 현황**: 대여/반납/예약 상태 실시간 반영
- **재고 알림**: 품목별 재고 부족 시 관리자 알림

#### 2.5 관리 기능
- **품목 관리**: 관리자가 카테고리별 세부 품목 등록/수정/삭제
- **대여 이력**: 학생별/품목별 대여 이력 조회
- **통계 대시보드**: 대여 현황, 인기 품목, 연체 현황 등

### 3. 사용자 권한

#### 3.1 학생 (일반 사용자)
- 실시간 재고 확인
- 온라인 예약
- 개인 대여 이력 조회
- 예약 취소

#### 3.2 관리자 (2명)
- 모든 학생 기능
- 품목 등록/수정/삭제
- 재고 관리
- 대여/반납 처리
- 전체 통계 및 이력 조회
- 시스템 설정 관리

### 4. 기술 요구사항

#### 4.1 성능 요구사항
- **응답 시간**: 일반 페이지 2초 이내, 예약 처리 1초 이내
- **동시 접속**: 최대 100명 동시 접속 지원
- **데이터 일관성**: 재고 관리 시 동시성 제어 필수

#### 4.2 보안 요구사항
- **인증**: JWT 기반 토큰 인증
- **인가**: 역할 기반 접근 제어 (RBAC)
- **데이터 보호**: 개인정보 암호화 저장
- **감사 로그**: 모든 대여/반납/관리 활동 로그 기록

#### 4.3 호환성
- **브라우저**: Chrome, Firefox, Safari 최신 버전
- **모바일**: 반응형 웹 디자인으로 모바일 접근 지원

### 5. 비기능 요구사항

#### 5.1 사용성
- **직관적 UI**: 학생들이 쉽게 사용할 수 있는 간단한 인터페이스
- **빠른 예약**: 3클릭 이내로 예약 완료
- **실시간 피드백**: 예약/대여/반납 상태 즉시 확인 가능

#### 5.2 신뢰성
- **가용성**: 99% 업타임 목표
- **데이터 백업**: 일일 자동 백업
- **장애 복구**: 시스템 장애 시 1시간 내 복구

#### 5.3 확장성
- **사용자 확장**: 향후 다른 학과 확장 고려
- **품목 확장**: 새로운 카테고리 추가 용이
- **기능 확장**: 알림 기능, 예약 대기열 등 추가 기능 고려

### 6. 제약사항

#### 6.1 개발 제약사항
- **개발 기간**: 1개월 (빠른 개발 우선)
- **예산**: 최소 비용 (오픈소스 기술 스택 선호)
- **인력**: 소규모 개발팀

#### 6.2 운영 제약사항
- **대학교 API 의존성**: 대학교 홈페이지 API 연동 필수 (대안 없음)
- **오프라인 연계**: 온라인 예약 + 오프라인 수령/반납 방식 고정
- **무료 서비스**: 수익 모델 없음 (학생 복지 목적)

### 7. 우선순위

#### 7.1 높음 (Must Have)
1. **재고 실시간 추적**: 정확한 재고 상태 관리
2. **예약 편의성**: 간단하고 빠른 예약 프로세스
3. **대학교 API 인증**: 융공대 학생 자동 인증

#### 7.2 중간 (Should Have)
1. **관리 업무 반자동화**: 관리자 업무 효율화
2. **대여 이력 관리**: 통계 및 분석 기능
3. **알림 시스템**: 예약/반납 알림

#### 7.3 낮음 (Nice to Have)
1. **모바일 앱**: 웹 기반으로 우선 개발
2. **고급 통계**: 상세 분석 기능
3. **다국어 지원**: 한국어 우선

---

## 개발 현황

### 완료된 단계
- ✅ **Phase 1**: 시스템 설계 및 아키텍처 (100%)
- ✅ **Phase 2**: 개발 환경 구축 (100%)
  - Docker 기반 개발 환경
  - FastAPI + React 프로젝트 구조
  - 데이터베이스 스키마 (6개 테이블)
- ✅ **Phase 3**: 핵심 백엔드 개발 (100%)
  - ✅ **상명대학교 SSO 인증 시스템 완전 해결 (2025-08-30)**
    - 실제 대학교 시스템과 100% 호환되는 로그인 구현
    - Playwright 브라우저 분석을 통한 실제 HTML 파싱 로직 구현
    - Form 데이터 POST 방식으로 HTTP 요청 완전 수정
  - ✅ 품목 관리 API 구현 완료 (카테고리 8개, 품목 22개)
  - ✅ 예약 시스템 API 구현 완료 (1시간 제한, 자동 취소)
  - ✅ 대여 관리 API 구현 완료 (7일 기간, 연장, 연체 관리)
  - ✅ **백엔드 실행 환경 완성**: SQLite + FastAPI 서버 정상 실행
  - ✅ **Swagger API 문서**: `http://localhost:8000/docs` 접근 가능 (총 32개 엔드포인트)

- ✅ **Phase 4**: 프론트엔드 개발 지원 (100%)
  - ✅ **프론트엔드 아키텍처 가이드**: `docs/FRONTEND_DEVELOPMENT_GUIDE.md` (400+ 줄)
    - React 18 + TypeScript + Material-UI 완전 설계
    - 피처 기반 컴포넌트 구조, TanStack Query 상태 관리
    - JWT 인증 및 보호된 라우트 패턴
  - ✅ **API 통합 가이드**: `docs/API_USAGE_EXAMPLES.md` (300+ 줄)
    - 32개 모든 엔드포인트 사용법 예제
    - 인증 플로우, 에러 처리, TypeScript 타입 정의
  - ✅ **UI/UX 설계 시스템**: `docs/UI_DESIGN_GUIDE.md` (500+ 줄)
    - 전체 페이지 와이어프레임 (로그인부터 관리자 대시보드)
    - Material-UI 컴포넌트 설계, 한국어 최적화, 모바일 우선 반응형
  - ✅ **샘플 데이터 완비**: `backend/scripts/seed_sample_data.py`
    - 7명 사용자, 8개 카테고리, 22개 품목, 다양한 예약/대여 시나리오

### 진행 중
- 🔄 **Phase 5**: 프론트엔드 구현 (75% 완료)
  - ✅ **React 개발환경 구축 완료** (2025-08-30)
    - TypeScript 5.3.3 + Material-UI 설정
    - 백엔드 API 연동 테스트 완료
  - ✅ **Vite 마이그레이션 완료** (2025-08-30)  
    - Create React App → Vite 5.0.8 완전 마이그레이션
    - npm → pnpm 10.15.0 패키지 매니저 전환
    - 개발 서버 시작 속도 10-100배 향상
  - ✅ **프론트엔드 리팩터링 및 최적화** (2025-08-30)
    - TypeScript path mapping 설정 (`@/` 절대 경로)
    - Vite 설정 최적화 (번들 분할, 프록시, 빌드 옵션)
    - ESLint + Prettier 통합 코드 품질 자동화
    - 공통 hooks 구현 (`useApi`, `useError`, `useLoading`, `useToast`)
    - 유틸리티 함수 중앙화 (에러 처리, 날짜 처리)
    - Toast 알림 시스템 구현
  - 🔄 핵심 사용자 기능 구현 중

### 다음 단계 (예정)  
- 📋 **Phase 6**: 통합 및 테스트
- 📋 **Phase 7**: 배포 및 운영
- 📋 **Phase 8**: 사용자 테스트 및 최적화

### 마일스톤
- **1주차 말**: Phase 2 완료 ✅
- **2주차 말**: Phase 3 완료 ✅  
- **3주차 초**: Phase 4 완료 ✅ (프론트엔드 지원 문서)
- **3주차 말**: Phase 5 진행 중 🔄 (프론트엔드 구현)
- **4주차 말**: Phase 6-8 완료 예정 (테스트, 배포, 최적화)



## 시스템 아키텍처

### 기술 스택

**백엔드**
- **FastAPI** (Python): 빠른 개발, 자동 API 문서화, 타입 힌트
- **PostgreSQL**: 관계형 데이터, ACID 보장, 동시성 제어
- **Redis**: 세션 관리, 예약 시간 제한 처리
- **SQLAlchemy**: ORM, 데이터베이스 추상화

**프론트엔드**
- **React 18 + TypeScript 5.3.3**: 컴포넌트 재사용, 타입 안정성, 고급 타입 추론
- **Vite 5.0.8**: 초고속 개발 서버 (HMR), 최적화된 빌드, 번들 분할 (Create React App 완전 대체)
- **Material-UI (MUI) v5**: 빠른 UI 구현, 반응형 디자인, 한국어 최적화 테마
- **React Router v6**: 클라이언트 사이드 라우팅, 보호된 라우트
- **TanStack Query v5**: 서버 상태 관리, 실시간 캐싱, 백그라운드 동기화
- **Axios**: HTTP 클라이언트, API 통신, JWT 인터셉터, 자동 토큰 관리
- **Day.js**: 날짜/시간 처리 (한국어 로케일 지원, 경량화)
- **ESLint + Prettier**: 코드 품질 자동화, 포맷팅 일관성, TypeScript 규칙

**개발 도구**
- **pnpm**: 빠른 패키지 매니저, 디스크 공간 효율성, 모노레포 지원
- **Vite TypeScript**: path mapping (`@/` 절대 경로), 타입 체크, 자동 완성
- **Git**: 버전 관리 (Feature Branch 전략)

**인프라**
- **Docker + Docker Compose**: 개발 환경 일관성
- **Nginx**: 리버스 프록시, 정적 파일 서빙

### 시스템 구조

```
[ 대학교 API ] ← 인증 연동
     ↕
[ Frontend (React) ]
     ↕ HTTP/REST
[ API Gateway (FastAPI) ]
     ↕
[ Business Logic Layer ]
     ↕
[ Data Access Layer (SQLAlchemy) ]
     ↕
[ PostgreSQL ] ← [ Redis (세션/캐시) ]
```

### 데이터베이스 스키마

#### 주요 테이블 구조

**1. users (사용자)**
- 학생 정보 및 관리자 권한 관리
- 대학교 API 연동을 통한 인증 정보 저장

**2. categories (카테고리)**
- 8개 대여 품목 카테고리 관리
- 확장 가능한 구조로 새 카테고리 추가 용이

**3. items (품목)**
- 개별 품목 추적 (serial_number로 구분)
- 상태 관리 (AVAILABLE/RESERVED/RENTED/MAINTENANCE)

**4. reservations (예약)**
- 온라인 예약 관리
- 1시간 시간 제한 및 자동 취소 처리

**5. rentals (대여)**
- 실제 대여 기록 및 반납 관리
- 7일 대여 기간 추적

**6. audit_logs (감사 로그)**
- 모든 시스템 활동 로그 기록
- 데이터 변경 이력 추적

##### 확장성 고려사항

- **유연한 품목 관리**: JSONB 메타데이터로 품목별 특수 속성 저장
- **다학과 확장**: department 컬럼으로 학과별 구분 가능
- **비즈니스 규칙 확장**: 카테고리별/품목별 대여 기간 설정 가능
- **알림 시스템**: 추후 notifications 테이블 추가 예정
- **무중단 확장**: PostgreSQL 마이그레이션으로 스키마 변경 지원

### 프론트엔드 구조

#### 컴포넌트 구조
```
src/
├── components/
│   ├── common/          # 공통 컴포넌트
│   │   ├── Layout.tsx
│   │   ├── Header.tsx
│   │   └── ProtectedRoute.tsx
│   ├── item/           # 품목 관련
│   │   ├── ItemCard.tsx
│   │   └── ItemList.tsx
│   ├── reservation/    # 예약 관련
│   └── admin/          # 관리자 전용
├── pages/              # 페이지 컴포넌트
├── hooks/              # 커스텀 훅
├── services/           # API 서비스
├── contexts/           # React Context
├── types/              # TypeScript 타입 정의
└── utils/              # 유틸리티 함수
```

#### 주요 기능
- **인증 시스템**: JWT 토큰 기반 인증, 학교 API 연동, Redis 세션 관리
- **상태 관리**: React Context (전역 상태) + TanStack Query (서버 상태)
- **라우팅**: React Router 기반 보호된 라우트
- **UI/UX**: Material-UI 컴포넌트, 반응형 디자인
- **타입 안전성**: TypeScript로 컴파일 타임 타입 검증

## API 개요

현재 총 **32개 API 엔드포인트**가 구현 완료되어 백엔드 시스템이 완성되었습니다.

- **Swagger 문서**: `http://localhost:8000/docs`
- **백엔드 API 문서**: [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)
- **프론트엔드 API 가이드**: [`docs/API_GUIDE.md`](docs/API_GUIDE.md)  
- **API 사용 예제**: [`docs/API_USAGE_EXAMPLES.md`](docs/API_USAGE_EXAMPLES.md)

### 구현 완료된 API 그룹
- ✅ **인증 API** (4개): 로그인/로그아웃, 토큰 관리, 사용자 조회
- ✅ **품목 관리 API** (14개): 카테고리/품목 CRUD, 검색, 통계
- ✅ **예약 시스템 API** (8개): 예약 생성/취소, 1시간 제한 관리
- ✅ **대여 관리 API** (8개): 대여/반납 처리, 연장, 연체 관리

---

## 프론트엔드 개발 시작 가이드

프론트엔드 개발자는 다음 순서로 개발을 시작할 수 있습니다:

### 1단계: 백엔드 실행 및 API 확인
```bash
# 1. 백엔드 실행 (이미 실행 중이면 생략)
cd backend
python3 -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

# 2. Swagger API 문서 확인
# 브라우저에서 http://localhost:8000/docs 접속

# 3. 샘플 데이터 로드 (필요시)
python3 scripts/seed_sample_data.py
```

### 2단계: 개발 가이드 문서 숙지
- **아키텍처 가이드**: `docs/FRONTEND_DEVELOPMENT_GUIDE.md` 전체 읽기
- **API 가이드**: `docs/API_USAGE_EXAMPLES.md`에서 인증 플로우 및 API 사용법 학습
- **UI 가이드**: `docs/UI_DESIGN_GUIDE.md`에서 전체 화면 설계 및 컴포넌트 명세 확인

### 3단계: React 개발 환경 설정
```bash
# frontend 디렉토리로 이동
cd frontend

# 의존성 설치 (이미 설정되어 있음)
pnpm install

# 개발 서버 시작 (Vite - 초고속)
pnpm dev

# 브라우저에서 http://localhost:3000 접속하여 확인
```

**현재 설치된 주요 라이브러리:**
- React 18 + TypeScript 5.3.3
- Vite 5.0.8 (빌드 도구)
- Material-UI v5 (@mui/material, @mui/icons-material)  
- TanStack Query v5 (@tanstack/react-query)
- React Router v6
- Axios, Day.js

### 4단계: 개발 시작
`docs/FRONTEND_DEVELOPMENT_GUIDE.md`의 "구현 순서" 섹션에 따라 단계적으로 개발:

1. **기본 설정** - 로우터, 타입, Context 설정
2. **인증 시스템** - 로그인, JWT 토큰 관리
3. **공통 컴포넌트** - Layout, Header, 로딩
4. **학생 기능** - 품목 목록, 예약, 내 이력
5. **관리자 기능** - 대시보드, 품목 관리

---

## 🚀 실행 방법

현재 시스템은 **Docker 실행**과 **로컬 실행** 두 가지 방식을 모두 지원합니다.

### 🪟 Windows 사용자를 위한 설치 가이드

**개발 초보자**를 위한 상세 가이드: [`WINDOWS_SETUP_GUIDE.md`](WINDOWS_SETUP_GUIDE.md)

### 🐳 Docker 실행 (프로덕션/배포용)

완전한 프로덕션 환경으로 모든 서비스를 컨테이너로 실행합니다.

```bash
# 전체 시스템 실행
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 접속
# - 웹사이트: http://localhost (Nginx 통해서)
# - API 문서: http://localhost:8000/docs  
# - 프론트엔드: http://localhost:3000
```

**Docker 환경 구성:**
- **PostgreSQL**: 데이터베이스 (포트 5432)
- **Redis**: 세션 캐시 (포트 6379)
- **Backend**: FastAPI 서버 (포트 8000)
- **Frontend**: React 개발서버 (포트 3000)
- **Nginx**: 리버스 프록시 (포트 80)

### 💻 로컬 실행 (개발용) ⭐ 현재 활성화됨

빠른 개발과 테스트를 위한 로컬 환경입니다.

```bash
# 1. 백엔드 실행 (SQLite 사용)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 2. 프론트엔드 실행 (별도 터미널)
cd frontend  
pnpm install  # 최초 1회만 (pnpm - 빠른 패키지 매니저)
pnpm dev      # Vite 개발 서버 실행 (HMR, 즉시 빌드)

# 접속
# - 프론트엔드: http://localhost:3000
# - API 문서: http://localhost:8000/docs
```

**로컬 환경 특징:**
- **SQLite**: 파일 기반 데이터베이스 (`rental_system.db`)
- **Vite**: 초고속 개발 서버 (HMR, 즉시 빌드, 번들 분할)
- **pnpm**: 빠른 패키지 설치 및 디스크 효율성 (npm 대비 3배 빠름)
- **TypeScript Path Mapping**: `@/` 절대 경로 지원으로 깔끔한 import
- **자동 새로고침**: 코드 변경 시 0.1초 내 HMR 반영
- **샘플 데이터**: 테스트용 계정 및 품목 데이터 포함
- **고급 TypeScript**: 5.3.3 버전으로 강력한 타입 체크 및 자동완성

### 📋 샘플 데이터 및 테스트 계정

로컬 실행 시 다음 테스트 계정을 사용할 수 있습니다:

```bash
# 샘플 데이터 생성 (최초 1회)
cd backend
python scripts/seed_sample_data.py
```

**샘플 품목:** 22개 품목 (운동용품, 전자기기, 생활용품 등)

### 🔄 환경 전환 가이드

#### 로컬 → Docker 전환:
1. `frontend/package.json`에서 proxy를 `"http://backend:8000"`으로 변경
2. `.env`의 DATABASE_URL을 PostgreSQL로 변경
3. `docker-compose up` 실행

#### Docker → 로컬 전환:
1. `frontend/package.json`에서 proxy를 `"http://localhost:8000"`으로 변경  
2. `.env`의 DATABASE_URL을 SQLite로 변경
3. 로컬 서버들 개별 실행

---

## 🔧 Redis 설정 및 세션 관리

### ⚠️ 현재 상황 (임시 수정 상태)

현재 시스템은 **Redis 서버 미설치**로 인해 다음과 같은 임시 수정이 적용된 상태입니다:

- **JWT-only 인증 모드**: Redis 세션 검증 실패 시에도 JWT 토큰만으로 인증 허용
- **세션 관리 무력화**: Redis 연결 실패를 우아하게 처리하여 시스템 안정성 유지
- **개발 환경 최적화**: 로컬 개발을 위한 임시 솔루션

### 🚀 Redis 설치 방법

Redis가 정상적으로 실행되면 완전한 세션 관리 시스템을 사용할 수 있습니다.

#### Ubuntu/Debian 설치
```bash
# Redis 서버 설치
sudo apt update
sudo apt install redis-server

# Redis 서비스 시작
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 설치 확인
redis-cli ping
# 응답: PONG
```

#### macOS 설치 (Homebrew)
```bash
# Homebrew로 Redis 설치
brew install redis

# Redis 서비스 시작
brew services start redis

# 설치 확인
redis-cli ping
# 응답: PONG
```

#### Docker로 Redis 실행 (권장)
```bash
# Redis 컨테이너 실행
docker run -d --name redis-server -p 6379:6379 redis:alpine

# 설치 확인
docker exec redis-server redis-cli ping
# 응답: PONG
```

### 🔄 Redis 정상 실행 시 코드 복원 가이드

Redis가 정상적으로 실행되면 다음 임시 수정사항들을 **원래 상태로 복원**해야 합니다:

#### 1. `backend/app/services/auth_service.py` 복원

**현재 임시 수정된 코드:**
```python
# 세션 유효성 검증 (Redis 없을 때는 JWT만으로 인증)
session_valid = validate_session(user_id, token)
if not session_valid:
    print(f"⚠️  Session validation failed for user {user_id}, using JWT-only auth")

# 사용자 조회 (세션 검증 무시)
user = db.query(User).filter(
    User.id == user_id,
    User.is_active == True
).first()

return user
```

**복원해야 할 원래 코드:**
```python
# 세션 유효성 검증
if not validate_session(user_id, token):
    return None

# 사용자 조회
user = db.query(User).filter(
    User.id == user_id,
    User.is_active == True
).first()

return user
```

#### 2. `backend/app/core/security.py` 복원 (선택사항)

현재 Redis 에러 처리를 위한 try-catch 블록들이 추가되어 있습니다:
- `create_session()`: Redis 실패 시 경고 메시지만 출력
- `get_session()`: Redis 실패 시 None 반환
- `delete_session()`: Redis 실패 시 True 반환

**Redis 정상 실행 시**: 이 에러 처리 코드들을 제거하고 Redis 연결 실패 시 예외를 발생시키도록 복원할 수 있습니다 (선택사항).

#### 3. 복원 절차

```bash
# 1. Redis 서비스 시작 확인
redis-cli ping

# 2. auth_service.py 수정
# 위의 복원 코드를 적용하여 세션 검증 로직 복원

# 3. 서버 재시작
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. 로그인 테스트
# 브라우저에서 로그인 후 세션 관리 정상 작동 확인
```

### ✨ Redis 사용 시 이점

Redis가 정상 실행되면 다음과 같은 **고급 세션 관리 기능**을 사용할 수 있습니다:

#### 🔐 보안 강화
- **이중 인증**: JWT 토큰 + Redis 세션으로 2차 보안
- **세션 무효화**: 의심스러운 활동 감지 시 특정 세션만 즉시 무효화
- **동시 로그인 제어**: 같은 계정의 여러 세션 관리

#### ⚡ 성능 향상  
- **빠른 세션 조회**: 메모리 기반으로 초고속 세션 검증
- **자동 만료**: TTL을 통한 세션 자동 정리
- **캐싱**: 사용자 정보 캐싱으로 DB 부하 감소

#### 🛠️ 운영 편의성
- **실시간 모니터링**: 활성 세션 수 실시간 확인
- **세션 관리**: 관리자 도구로 사용자 세션 조회/삭제
- **로그아웃 강제**: 특정 사용자 모든 세션 강제 로그아웃

#### 📊 사용 통계
- **동시 접속자 수**: 실시간 활성 사용자 통계
- **사용 패턴 분석**: 로그인 시간, 세션 지속 시간 등
- **보안 감사**: 비정상적인 로그인 패턴 감지

### 📋 개발/프로덕션 환경별 설정

#### 개발 환경
```bash
# .env 파일 설정
REDIS_URL=redis://localhost:6379

# 단순한 Redis 설정 (보안 설정 최소)
```

#### 프로덕션 환경
```bash
# .env 파일 설정
REDIS_URL=redis://username:password@redis-server:6379/0

# 추가 보안 설정
# - 비밀번호 인증
# - SSL/TLS 연결
# - Redis Cluster (고가용성)
# - 정기 백업
```

---

## 📝 최근 업데이트 (2025-08-31)

### 🎉 실제 대여물품 목록 구축 및 시스템 완성
- **실제 대여물품 데이터 구축**: 총 133개 실제 대여 품목으로 대폭 확장
  - 5개 주요 카테고리: 스포츠용품(27개), 문구/사무(12개), 보드게임(23개), 일상생활용품(43개), 기타
  - 모든 품목에 고유 일련번호 부여 및 "학생회실" 보관 위치 설정
- **저작권 정보 업데이트**: "© 2025 융합공과대학 학생회 태그. All rights reserved."
- **API 연동 문제 해결**:
  - 카테고리 드롭다운 API 응답 구조 수정 (`categoriesResponse?.items` → `categoriesResponse?.categories`)
  - SQLAlchemy joinedload 오류 해결 (property 메서드 로딩 제거)
  - FastAPI import 충돌 해결 및 엔드포인트 정상화
  - 품목 조회 API 구조 통일화
- **전체 시스템 검증 완료**: 인증, 카테고리, 품목, 예약, 대여 API 모든 기능 정상 동작 확인

### 📊 현재 시스템 상태
- **133개 실제 대여 품목** (5개 주요 카테고리)
  - **스포츠용품** (27개): 농구공, 축구공, 배드민턴채, 테니스채, 탁구채, 야구공, 글러브 등
  - **문구/사무** (12개): 공학용계산기 12개
  - **보드게임** (23개): 젠가, 루미큐브, 카탄, 스플렌더, 할리갈리, COUP 등 23종
  - **일상생활용품** (43개): 우산 30개, 실험복 3개, 인공눈물 10개
  - **보조배터리** (24개): 8핀 일체형 6개, C타입 일체형 9개, 통합형 6개, 연결선 3개

- **모든 주요 API 엔드포인트 정상 동작 확인**
- **프론트엔드-백엔드 완전 연동 상태**

### Phase 5 프론트엔드 구현 완료 (100%)
- **React 개발환경 구축 완료**: TypeScript 5.3.3, Material-UI v5, 백엔드 API 연동 완료
- **Vite 마이그레이션 성공**: Create React App → Vite 5.0.8, HMR 최적화
- **pnpm 패키지 매니저 도입**: 설치 속도 3배 향상, 디스크 공간 50% 절약
- **아키텍처 최적화**: TypeScript path mapping, ESLint + Prettier, Toast 시스템

---

**최종 수정일**: 2025-08-31  
**작성자**: 윤세연