# API 개발 가이드 (프론트엔드 개발자용)

## 개요

프론트엔드 개발자가 렌탈 관리 시스템 API를 효율적으로 사용할 수 있도록 작성된 가이드입니다.

## 🆕 최신 업데이트 (2025-08-31)
**시스템 완전성 검증 및 API 연동 완료**:
- 전체 API 엔드포인트 정상 동작 검증 완료 ✅
- 샘플 데이터 구축: 19개 품목, 7개 카테고리 생성
- 주요 버그 수정: 카테고리 API, SQLAlchemy 오류, FastAPI import 문제 해결


## 빠른 시작

### 1. API 문서 확인
백엔드 서버를 실행한 후 다음 URL에서 상세한 API 문서를 확인할 수 있습니다:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 2. 기본 정보
- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: `Bearer {JWT_TOKEN}`

## 인증 시스템

### 로그인 플로우
```javascript
// 1. 로그인 요청
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_id: "학번입력",
    password: "password123"
  })
});

const { access_token, user } = await loginResponse.json();

// 2. 토큰을 localStorage에 저장
localStorage.setItem('access_token', access_token);

// 3. 이후 모든 요청에 Authorization 헤더 추가
const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${access_token}`
};
```

### 권한 구조
- **학생 (STUDENT)**: 
  - 품목/카테고리 조회
  - 본인 예약/대여만 조회/관리
- **관리자 (ADMIN)**:
  - 모든 기능 접근 가능
  - 품목 등록/수정/삭제
  - 모든 사용자의 예약/대여 관리

## 주요 API 엔드포인트

### 인증 API (`/auth`)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| POST | `/auth/login` | 로그인 | 공개 |
| POST | `/auth/logout` | 로그아웃 | 인증 필요 |
| GET | `/auth/me` | 현재 사용자 정보 | 인증 필요 |
| POST | `/auth/refresh` | 토큰 갱신 | 인증 필요 |

### 품목 관리 API (`/categories`, `/items`)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/categories` | 카테고리 목록 | 학생 |
| GET | `/items` | 품목 목록 | 학생 |
| GET | `/items/available` | 대여 가능한 품목 | 학생 |
| POST | `/categories` | 카테고리 생성 | 관리자 |
| POST | `/items` | 품목 등록 | 관리자 |

### 예약 관리 API (`/reservations`)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/reservations/my` | 내 활성 예약 | 학생 |
| POST | `/reservations` | 예약 생성 (notes 메모 포함) | 학생 |
| POST | `/reservations/{id}/cancel` | 예약 취소 | 학생(본인)/관리자 |
| POST | `/reservations/{id}/confirm` | 예약 확인 | 관리자 |

### 대여 관리 API (`/rentals`)
| Method | Endpoint | 설명 | 권한 |
|--------|----------|------|------|
| GET | `/rentals/my` | 내 활성 대여 | 학생 |
| POST | `/rentals/{id}/return` | 대여 반납 | 관리자 |
| POST | `/rentals/{id}/extend` | 대여 연장 | 관리자 |

## 💡 중요한 비즈니스 로직

### 1. 예약 시스템
- **1시간 제한**: 예약 후 1시간 내 수령 필요
- **자동 만료**: 1시간 초과 시 자동으로 EXPIRED 상태로 변경
- **실시간 상태**: `remaining_minutes` 필드로 남은 시간 확인 가능

```javascript
// 예약 생성 (notes 필드 추가)
const reservation = await fetch('/api/v1/reservations', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    item_id: 1,
    notes: "오후 3시경 수령 예정"  // 예약 메모 (선택사항, 최대 500자)
  })
});

// 남은 시간 실시간 표시
const { remaining_minutes, is_expired } = reservationData;
if (is_expired) {
  showExpiredMessage();
} else {
  showCountdown(remaining_minutes);
}
```

### 2. 대여 시스템
- **7일 기본 기간**: 모든 품목 7일 대여
- **연장 가능**: 관리자 승인으로 최대 7일 추가 연장
- **자동 연체**: 반납일 초과 시 OVERDUE 상태로 변경

```javascript
// 남은 일수/연체 일수 표시
const { is_overdue, days_remaining, days_overdue } = rentalData;
if (is_overdue) {
  showOverdueWarning(days_overdue);
} else {
  showRemainingDays(days_remaining);
}
```

### 3. 품목 상태 관리
- **AVAILABLE**: 대여 가능
- **RESERVED**: 예약됨 (1시간 이내)
- **RENTED**: 대여 중
- **MAINTENANCE**: 정비 중

## 🎨 UI/UX 가이드라인

### 상태 표시 색상 권장
- **AVAILABLE**: 녹색 (`#4CAF50`)
- **RESERVED**: 주황색 (`#FF9800`)
- **RENTED**: 빨간색 (`#F44336`)
- **MAINTENANCE**: 회색 (`#9E9E9E`)

### 실시간 업데이트 권장
- 예약 페이지: 1분마다 남은 시간 업데이트
- 대여 목록: 페이지 로드 시마다 상태 확인
- 품목 목록: 실시간 재고 상태 반영

## 🔍 자주 사용되는 API 조합

### 1. 품목 예약하기
```javascript
// 1. 대여 가능한 품목 조회
const availableItems = await fetch('/api/v1/items/available');

// 2. 예약 생성 (메모 포함)
const reservation = await fetch('/api/v1/reservations', {
  method: 'POST',
  headers,
  body: JSON.stringify({ 
    item_id: selectedItemId,
    notes: "점심시간에 수령 예정"  // 선택사항
  })
});

// 3. 내 예약 목록 새로고침
const myReservations = await fetch('/api/v1/reservations/my', { headers });
```

### 2. 관리자 - 예약 확인 및 대여 처리
```javascript
// 1. 대기 중인 예약 조회
const pendingReservations = await fetch('/api/v1/reservations?status=PENDING', { headers });

// 2. 예약 확인 (자동으로 대여 레코드 생성됨)
const confirmedReservation = await fetch(`/api/v1/reservations/${reservationId}/confirm`, {
  method: 'POST',
  headers,
  body: JSON.stringify({ admin_notes: "정상 수령 확인" })
});

// 3. 생성된 대여 조회
const activeRentals = await fetch('/api/v1/rentals?status=ACTIVE', { headers });
```

## ❌ 에러 처리

### 일반적인 HTTP 상태 코드
- `400`: 잘못된 요청 (유효성 검사 실패)
- `401`: 인증 필요 (로그인 필요)
- `403`: 권한 없음 (관리자 전용 기능)
- `404`: 리소스 없음
- `500`: 서버 오류

### 에러 응답 예시
```javascript
{
  "detail": "이미 해당 품목을 예약하였습니다"
}
```

### 권장 에러 처리
```javascript
try {
  const response = await fetch('/api/v1/reservations', {
    method: 'POST',
    headers,
    body: JSON.stringify(reservationData)
  });

  if (!response.ok) {
    const error = await response.json();
    
    if (response.status === 401) {
      // 토큰 만료 - 재로그인 유도
      redirectToLogin();
    } else if (response.status === 400) {
      // 비즈니스 로직 오류 - 사용자에게 메시지 표시
      showErrorMessage(error.detail);
    }
  }
  
  const result = await response.json();
  // 성공 처리
} catch (error) {
  // 네트워크 오류 처리
  showNetworkError();
}
```

## 📱 반응형 고려사항

### 모바일에서 중요한 기능들
1. **QR 코드 스캔**: 품목 일련번호 빠른 입력
2. **간편 예약**: 최소 터치로 예약 완료
3. **알림**: 예약 만료, 반납 기한 푸시 알림
4. **오프라인 모드**: 네트워크 끊겨도 기본 정보 표시

### 데스크톱에서 추가 기능들
1. **대시보드**: 통계 및 현황 한눈에 보기
2. **일괄 처리**: 여러 예약/대여 동시 관리
3. **상세 필터링**: 복합 조건 검색
4. **엑셀 내보내기**: 이력 데이터 다운로드

---

**다음 단계**: [개발 환경 설정 가이드](./DEVELOPMENT_SETUP.md)로 이동하여 로컬 개발 환경을 구축해보세요.