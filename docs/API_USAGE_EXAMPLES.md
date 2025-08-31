# API 사용 예제 및 테스트 가이드

## 📋 개요

렌탈 관리 시스템의 백엔드 API와 상호작용하는 방법을 단계별로 안내합니다.

**API Base URL**: `http://localhost:8000/api/v1`  
**Swagger 문서**: `http://localhost:8000/docs`

⚠️ **중요**: 현재 Redis 없이 JWT 전용 인증으로 운영 중 (개발 환경)

---

## 🔐 인증 (Authentication)

### 🆕 현재 인증 시스템 상태 (2025-08-31 업데이트)

**✅ 시스템 완전성 검증 완료**:
- 모든 API 엔드포인트 정상 동작 확인
- 로그인/로그아웃 프로세스 완전 검증
- JWT 토큰 기반 인증 시스템 정상 작동


**🎯 주요 수정사항**:
- 카테고리 API 응답 구조 수정 완료
- SQLAlchemy joinedload 오류 해결
- FastAPI import 충돌 문제 해결
- 프론트엔드-백엔드 API 연동 완전 정상화

### 1. 로그인 API

```javascript
// POST /api/v1/auth/login
const loginExample = async () => {
  try {
    // 프론트엔드에서는 apiClient.post() 직접 사용 (ApiResponse 래퍼 제거)
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        student_id: 'your_student_id',  // 실제 학번 입력
        password: 'your_password'       // 실제 대학교 시스템 비밀번호
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // 성공 응답 (직접 LoginResponse 형식)
      console.log('로그인 성공:', data);
      // {
      //   access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      //   token_type: "bearer", 
      //   user: {
      //     id: 3,
      //     student_id: "your_student_id",
      //     name: "사용자명",
      //     role: "STUDENT",
      //     department: "전공명"
      //   }
      // }
      
      // JWT 토큰을 저장 
      localStorage.setItem('token', data.access_token);
      return data;
    } else {
      console.error('로그인 실패:', data.detail);
    }
  } catch (error) {
    console.error('네트워크 오류:', error);
  }
};
```

### 2. 인증이 필요한 API 호출

```javascript
// 저장된 토큰으로 인증된 요청 보내기
const authenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });
};

// 사용 예제
const getCurrentUser = async () => {
  const response = await authenticatedRequest('http://localhost:8000/api/v1/auth/me');
  return response.json();
};
```

---

## 📦 품목 관리 (Items)

### 1. 대여 가능한 품목 조회

```javascript
// GET /api/v1/items/available
const getAvailableItems = async (categoryId = null) => {
  let url = 'http://localhost:8000/api/v1/items/available';
  
  if (categoryId) {
    url += `?category_id=${categoryId}`;
  }
  
  try {
    const response = await authenticatedRequest(url);
    const items = await response.json();
    
    console.log('대여 가능한 품목들:', items);
    // [
    //   {
    //     id: 1,
    //     name: "축구공",
    //     serial_number: "SPORT-001",
    //     status: "AVAILABLE",
    //     category: { name: "운동용품" },
    //     item_metadata: { "브랜드": "나이키", "크기": "5호" }
    //   },
    //   ...
    // ]
    
    return items;
  } catch (error) {
    console.error('품목 조회 실패:', error);
  }
};
```

### 2. 품목 검색 및 필터링

```javascript
// GET /api/v1/items with filters
const searchItems = async (searchQuery, categoryId = null, status = null) => {
  const params = new URLSearchParams();
  
  if (searchQuery) params.append('search', searchQuery);
  if (categoryId) params.append('category_id', categoryId);
  if (status) params.append('status', status);
  
  const response = await authenticatedRequest(
    `http://localhost:8000/api/v1/items?${params}`
  );
  
  const result = await response.json();
  
  console.log('검색 결과:', result);
  // {
  //   items: [...],
  //   total: 15,
  //   page: 1,
  //   page_size: 100
  // }
  
  return result;
};

// 사용 예제들
searchItems('보조배터리');  // 이름으로 검색
searchItems(null, 2, 'AVAILABLE');  // 전자기기 카테고리의 대여 가능한 품목
```

---

## 📂 카테고리 관리

### 1. 카테고리 목록 조회

```javascript
// GET /api/v1/categories
const getCategories = async () => {
  const response = await authenticatedRequest('http://localhost:8000/api/v1/categories');
  const result = await response.json();
  
  console.log('카테고리 목록:', result);
  // {
  //   categories: [
  //     { id: 1, name: "운동용품", description: "스포츠 및 운동 관련 용품들" },
  //     { id: 2, name: "전자기기", description: "보조배터리, 계산기 등 전자제품" },
  //     ...
  //   ],
  //   total: 8
  // }
  
  return result;
};
```

---

## 🔖 예약 시스템 (Reservations)

### 1. 예약 생성

```javascript
// POST /api/v1/reservations
const createReservation = async (itemId, notes = null) => {
  try {
    const response = await authenticatedRequest('http://localhost:8000/api/v1/reservations', {
      method: 'POST',
      body: JSON.stringify({
        item_id: itemId,
        notes: notes  // 예약 메모 (선택사항, 최대 500자)
      })
    });
    
    const reservation = await response.json();
    
    if (response.ok) {
      console.log('예약 성공:', reservation);
      // {
      //   id: 1,
      //   item: { name: "보조배터리", serial_number: "ELEC-001" },
      //   reserved_at: "2025-08-30T12:40:59",
      //   expires_at: "2025-08-30T13:40:59",  // 1시간 후 만료
      //   status: "PENDING",
      //   notes: "테스트 예약입니다",  // 예약 시 입력한 메모
      //   time_remaining_minutes: 60
      // }
      
      // 예약 성공 후 품목 목록 새로고침 필요
      return reservation;
    } else {
      console.error('예약 실패:', reservation.detail);
      // 가능한 에러들:
      // - "이미 예약된 품목입니다"
      // - "대여 불가능한 품목입니다"
      // - "동시 예약 한도를 초과했습니다"
    }
  } catch (error) {
    console.error('예약 요청 실패:', error);
  }
};
```

### 2. 내 활성 예약 조회

```javascript
// GET /api/v1/reservations/my
const getMyActiveReservations = async () => {
  const response = await authenticatedRequest('http://localhost:8000/api/v1/reservations/my');
  const reservations = await response.json();
  
  console.log('내 활성 예약들:', reservations);
  // [
  //   {
  //     id: 1,
  //     item: { name: "보조배터리", serial_number: "ELEC-001" },
  //     expires_at: "2025-08-30T13:40:59",
  //     time_remaining_minutes: 45,  // 남은 시간 (분)
  //     is_expired: false,
  //     status: "PENDING"
  //   }
  // ]
  
  return reservations;
};
```

### 3. 예약 취소

```javascript
// POST /api/v1/reservations/{id}/cancel
const cancelReservation = async (reservationId, reason = null) => {
  try {
    const response = await authenticatedRequest(
      `http://localhost:8000/api/v1/reservations/${reservationId}/cancel`,
      {
        method: 'POST',
        body: JSON.stringify({
          reason: reason || '사용자 취소'
        })
      }
    );
    
    const result = await response.json();
    
    if (response.ok) {
      console.log('예약 취소 완료:', result);
      // 품목이 다시 AVAILABLE 상태로 변경됨
      return result;
    } else {
      console.error('예약 취소 실패:', result.detail);
    }
  } catch (error) {
    console.error('예약 취소 요청 실패:', error);
  }
};
```

### 4. 예약 타이머 구현

```javascript
// 실시간 예약 타이머 컴포넌트 예제
const ReservationTimer = ({ expiresAt, onExpire }) => {
  const [timeLeft, setTimeLeft] = useState(0);
  
  useEffect(() => {
    const updateTimer = () => {
      const now = new Date().getTime();
      const expiry = new Date(expiresAt).getTime();
      const difference = expiry - now;
      
      if (difference > 0) {
        setTimeLeft(difference);
      } else {
        setTimeLeft(0);
        onExpire?.();
      }
    };
    
    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    
    return () => clearInterval(interval);
  }, [expiresAt, onExpire]);
  
  const formatTime = (milliseconds) => {
    const minutes = Math.floor(milliseconds / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  
  const isUrgent = timeLeft < 10 * 60 * 1000; // 10분 미만
  
  return (
    <div className={`timer ${isUrgent ? 'urgent' : ''}`}>
      남은 시간: {formatTime(timeLeft)}
      {isUrgent && ' ⚠️ 곧 만료됩니다!'}
    </div>
  );
};
```

---

## 📅 대여 관리 (Rentals)

### 1. 내 활성 대여 조회

```javascript
// GET /api/v1/rentals/my
const getMyActiveRentals = async () => {
  const response = await authenticatedRequest('http://localhost:8000/api/v1/rentals/my');
  const rentals = await response.json();
  
  console.log('내 활성 대여들:', rentals);
  // [
  //   {
  //     id: 1,
  //     item: { name: "배드민턴 라켓", serial_number: "SPORT-003" },
  //     rental_date: "2025-08-23",
  //     due_date: "2025-08-30",
  //     days_remaining: 0,  // 반납 예정일까지 남은 일수
  //     is_overdue: false,
  //     status: "ACTIVE"
  //   },
  //   {
  //     id: 2,
  //     item: { name: "카탄", serial_number: "GAME-002" },
  //     rental_date: "2025-08-22",
  //     due_date: "2025-08-29",
  //     days_remaining: -1,  // 음수면 연체
  //     is_overdue: true,
  //     status: "OVERDUE"
  //   }
  // ]
  
  return rentals;
};
```

---

## ⚠️ 에러 처리 패턴

### 1. 일반적인 에러 응답 형식

```javascript
// 에러 응답 예제들
const handleApiErrors = (response, errorData) => {
  switch (response.status) {
    case 400:
      // 잘못된 요청
      console.error('요청 오류:', errorData.detail);
      // 예: "품목이 이미 예약되었습니다"
      break;
      
    case 401:
      // 인증 실패
      console.error('인증 실패:', errorData.detail);
      localStorage.removeItem('token');
      // 로그인 페이지로 리다이렉트
      window.location.href = '/login';
      break;
      
    case 403:
      // 권한 없음
      console.error('권한 없음:', errorData.detail);
      // 예: "관리자 권한이 필요합니다"
      break;
      
    case 404:
      // 리소스 없음
      console.error('찾을 수 없음:', errorData.detail);
      // 예: "품목을 찾을 수 없습니다"
      break;
      
    case 422:
      // 유효성 검증 실패
      console.error('입력 오류:', errorData.detail);
      // 예: 필드별 상세 오류 정보
      break;
      
    default:
      console.error('서버 오류:', errorData.detail || '알 수 없는 오류');
  }
};
```

### 2. 재사용 가능한 API 클라이언트

```javascript
// API 클라이언트 클래스
class RentalAPIClient {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('token');
  }
  
  // 기본 요청 메서드
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
      ...options,
    };
    
    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API 요청 실패 [${endpoint}]:`, error.message);
      throw error;
    }
  }
  
  // 인증 관련
  async login(studentId, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, password }),
    });
    
    this.token = data.access_token;
    localStorage.setItem('token', this.token);
    return data;
  }
  
  async getCurrentUser() {
    // ⚠️ 현재 Redis 세션 검증 실패 시 JWT만으로 인증 (개발환경)
    return this.request('/auth/me');
  }
  
  async logout() {
    // ⚠️ 현재 Redis 세션 삭제 실패해도 로컬스토리지 토큰만 삭제 (개발환경)
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } catch (error) {
      console.warn('서버 로그아웃 실패, 로컬 토큰만 삭제:', error.message);
    } finally {
      this.token = null;
      localStorage.removeItem('token');
    }
  }
  
  // 품목 관련
  async getAvailableItems(categoryId = null) {
    const params = categoryId ? `?category_id=${categoryId}` : '';
    return this.request(`/items/available${params}`);
  }
  
  async getItem(itemId) {
    return this.request(`/items/${itemId}`);
  }
  
  // 예약 관련
  async createReservation(itemId, notes = null) {
    return this.request('/reservations', {
      method: 'POST',
      body: JSON.stringify({ 
        item_id: itemId, 
        notes  // 예약 메모 (선택사항, 최대 500자)
      }),
    });
  }
  
  async getMyReservations() {
    return this.request('/reservations/my');
  }
  
  async cancelReservation(reservationId, reason = null) {
    return this.request(`/reservations/${reservationId}/cancel`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }
  
  // 대여 관련
  async getMyRentals() {
    return this.request('/rentals/my');
  }
}

// 사용 예제
const api = new RentalAPIClient();

// 로그인
try {
  const user = await api.login('your_student_id', 'your_password');
  console.log('로그인 성공:', user);
} catch (error) {
  console.error('로그인 실패:', error.message);
}

// 품목 조회
try {
  const items = await api.getAvailableItems();
  console.log('대여 가능한 품목:', items);
} catch (error) {
  console.error('품목 조회 실패:', error.message);
}
```

---

## 🧪 테스트 시나리오

### 1. 완전한 예약-대여 플로우 테스트

```javascript
// 전체 사용자 플로우 테스트
const testCompleteFlow = async () => {
  const api = new RentalAPIClient();
  
  try {
    // 1. 로그인
    console.log('1. 로그인 중...');
    const user = await api.login('your_student_id', 'your_password');
    console.log('✅ 로그인 성공:', user.user.name);
    
    // 2. 대여 가능한 품목 조회
    console.log('2. 품목 조회 중...');
    const items = await api.getAvailableItems();
    const availableItem = items.find(item => item.status === 'AVAILABLE');
    console.log('✅ 대여 가능한 품목:', availableItem.name);
    
    // 3. 예약 생성
    console.log('3. 예약 생성 중...');
    const reservation = await api.createReservation(
      availableItem.id, 
      '테스트 예약입니다'
    );
    console.log('✅ 예약 성공:', reservation.id);
    
    // 4. 내 예약 확인
    console.log('4. 예약 확인 중...');
    const myReservations = await api.getMyReservations();
    console.log('✅ 내 예약:', myReservations.length, '개');
    
    // 5. 예약 취소 (테스트를 위해)
    console.log('5. 예약 취소 중...');
    await api.cancelReservation(reservation.id, '테스트 완료');
    console.log('✅ 예약 취소 완료');
    
    console.log('🎉 전체 플로우 테스트 성공!');
    
  } catch (error) {
    console.error('❌ 테스트 실패:', error.message);
  }
};

// 테스트 실행
testCompleteFlow();
```

### 2. 예약 타이머 동작 테스트

```javascript
// 예약 만료 시간 테스트
const testReservationTimer = async () => {
  const api = new RentalAPIClient();
  
  try {
    // 로그인 및 예약 생성
    await api.login('your_student_id', 'your_password');
    const items = await api.getAvailableItems();
    const reservation = await api.createReservation(items[0].id);
    
    console.log('예약 생성:', reservation.id);
    console.log('만료 시간:', reservation.expires_at);
    
    // 1분마다 남은 시간 확인
    const timer = setInterval(async () => {
      try {
        const myReservations = await api.getMyReservations();
        const currentReservation = myReservations.find(r => r.id === reservation.id);
        
        if (currentReservation) {
          console.log(`남은 시간: ${currentReservation.time_remaining_minutes}분`);
          
          if (currentReservation.is_expired) {
            console.log('⏰ 예약이 만료되었습니다!');
            clearInterval(timer);
          }
        } else {
          console.log('예약을 찾을 수 없습니다 (만료됨)');
          clearInterval(timer);
        }
      } catch (error) {
        console.error('타이머 확인 실패:', error.message);
        clearInterval(timer);
      }
    }, 60000); // 1분마다
    
  } catch (error) {
    console.error('예약 타이머 테스트 실패:', error.message);
  }
};
```

### 3. 에러 상황 테스트

```javascript
// 다양한 에러 상황 테스트
const testErrorScenarios = async () => {
  const api = new RentalAPIClient();
  
  // 잘못된 로그인
  try {
    await api.login('invalid_id', 'wrong_password');
  } catch (error) {
    console.log('✅ 잘못된 로그인 에러 처리:', error.message);
  }
  
  // 토큰 없이 API 호출
  api.token = null;
  try {
    await api.getMyReservations();
  } catch (error) {
    console.log('✅ 인증 없는 요청 에러 처리:', error.message);
  }
  
  // 올바른 로그인 후
  await api.login('2024101', 'test123');
  
  // 존재하지 않는 품목 예약
  try {
    await api.createReservation(99999);
  } catch (error) {
    console.log('✅ 존재하지 않는 품목 에러 처리:', error.message);
  }
  
  // 이미 예약된 품목 중복 예약
  try {
    const items = await api.getAvailableItems();
    const reservedItem = items.find(item => item.status === 'RESERVED');
    if (reservedItem) {
      await api.createReservation(reservedItem.id);
    }
  } catch (error) {
    console.log('✅ 중복 예약 에러 처리:', error.message);
  }
};
```

---

## 💡 프론트엔드 구현 팁

### 1. 실시간 상태 업데이트

```javascript
// React Query를 사용한 실시간 데이터 동기화
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const useItems = () => {
  return useQuery({
    queryKey: ['items'],
    queryFn: () => api.getAvailableItems(),
    staleTime: 30 * 1000, // 30초
    refetchOnWindowFocus: true,
    refetchInterval: 60 * 1000, // 1분마다 새로고침
  });
};

const useCreateReservation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (itemId) => api.createReservation(itemId),
    onSuccess: () => {
      // 관련 캐시 무효화로 자동 새로고침
      queryClient.invalidateQueries(['items']);
      queryClient.invalidateQueries(['reservations']);
    },
  });
};
```

### 2. 토스트 알림 시스템

```javascript
// 사용자 피드백을 위한 알림
const useToast = () => {
  const showSuccess = (message) => {
    // 성공 토스트 표시
    toast.success(message);
  };
  
  const showError = (error) => {
    // 에러 메시지 표시
    toast.error(error.message || '오류가 발생했습니다');
  };
  
  return { showSuccess, showError };
};

// 예약 생성 시 사용
const handleReserve = async (itemId) => {
  const { showSuccess, showError } = useToast();
  
  try {
    await api.createReservation(itemId);
    showSuccess('예약이 완료되었습니다! 1시간 내에 수령해 주세요.');
  } catch (error) {
    showError(error);
  }
};
```

---

## 📊 샘플 데이터 활용

현재 데이터베이스에 다음 테스트 데이터가 준비되어 있습니다:

### 테스트 계정들
```
테스트 계정:
- 실제 대학교 계정을 사용하여 테스트하세요
```

### 품목 상태별 샘플 데이터
```
AVAILABLE 품목: 축구공, 농구공, 탁구라켓 등 15개
RESERVED 품목: 보조배터리 (ELEC-001) - 5분 후 만료
RENTED 품목: 배드민턴 라켓, 무선마우스, 카탄, 캠핑의자 등 4개
```

이를 활용하여 다양한 UI 상태를 테스트할 수 있습니다.

---

## 🚀 다음 단계

1. **Postman 컬렉션**: API 테스트를 위한 Postman 컬렉션 파일 생성
2. **자동화 테스트**: Jest/Vitest를 사용한 API 통합 테스트
3. **성능 테스트**: 동시 다발적 예약 요청 테스트
4. **실시간 기능**: WebSocket 또는 Server-Sent Events 적용 검토

현재 모든 API가 정상 작동하므로 프론트엔드 개발을 바로 시작할 수 있습니다!