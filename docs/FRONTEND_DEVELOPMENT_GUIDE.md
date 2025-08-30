# 프론트엔드 개발 가이드

## 📋 개요

융합공과대학 렌탈 관리 시스템의 프론트엔드 개발을 위한 종합 가이드입니다.

**백엔드 API**: `http://localhost:8000/docs` (Swagger 문서)  
**총 32개 엔드포인트**: 인증, 카테고리, 품목, 예약, 대여 관리

---

## 🏗️ 시스템 아키텍처

### 기술 스택

```typescript
Frontend Stack:
├── React 18 + TypeScript     // 컴포넌트 기반 UI 개발
├── Material-UI v5            // 한국어 최적화 디자인 시스템
├── TanStack Query v5         // 서버 상태 관리 & 캐싱
├── React Router v6           // 클라이언트 사이드 라우팅
├── React Hook Form           // 폼 관리 및 검증
├── Day.js (Korean locale)    // 날짜/시간 처리
├── Create React App          // 빠른 개발 환경 구성
└── webpack-dev-server v5.2.2 // 개발 서버 (devDependencies)
```

### 아키텍처 패턴

**Feature-based Architecture** 채택
```
src/
├── features/               # 기능별 모듈화
│   ├── auth/              # 인증 관련
│   ├── items/             # 품목 관리
│   ├── reservations/      # 예약 시스템
│   ├── rentals/           # 대여 관리
│   └── admin/             # 관리자 기능
├── shared/                # 공통 컴포넌트
│   ├── components/        # 재사용 가능한 UI 컴포넌트
│   ├── hooks/             # 커스텀 훅
│   ├── services/          # API 클라이언트
│   └── utils/             # 유틸리티 함수
└── types/                 # TypeScript 타입 정의
```

---

## 🔐 인증 시스템

### JWT 기반 인증 플로우

```typescript
// src/features/auth/hooks/useAuth.ts
export const useAuth = () => {
  const queryClient = useQueryClient();
  
  const login = useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      const response = await authAPI.login(credentials);
      localStorage.setItem('token', response.access_token);
      return response;
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['currentUser'], data.user);
    }
  });
  
  const logout = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      localStorage.removeItem('token');
      queryClient.clear();
    }
  });
  
  return { login, logout };
};
```

### 권한 기반 라우팅

```typescript
// src/shared/components/ProtectedRoute.tsx
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'STUDENT' | 'ADMIN';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { data: currentUser, isLoading } = useCurrentUser();
  
  if (isLoading) return <LoadingSpinner />;
  if (!currentUser) return <Navigate to="/login" />;
  if (requiredRole && currentUser.role !== requiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  return <>{children}</>;
};
```

---

## 📱 라우팅 구조

```typescript
// src/App.tsx
const AppRoutes = () => (
  <Routes>
    {/* 공개 라우트 */}
    <Route path="/login" element={<LoginPage />} />
    
    {/* 보호된 라우트 */}
    <Route path="/" element={
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    }>
      {/* 학생 & 관리자 공통 */}
      <Route index element={<ItemsPage />} />
      <Route path="my-reservations" element={<MyReservationsPage />} />
      <Route path="my-rentals" element={<MyRentalsPage />} />
      
      {/* 관리자 전용 */}
      <Route path="admin/*" element={
        <ProtectedRoute requiredRole="ADMIN">
          <AdminRoutes />
        </ProtectedRoute>
      } />
    </Route>
  </Routes>
);
```

---

## 🎨 컴포넌트 설계 패턴

### 1. ItemCard 컴포넌트 (핵심)

```typescript
// src/features/items/components/ItemCard.tsx
interface ItemCardProps {
  item: Item;
  onReserve?: (itemId: number) => void;
  showAdminActions?: boolean;
}

export const ItemCard: React.FC<ItemCardProps> = ({ 
  item, 
  onReserve, 
  showAdminActions 
}) => {
  const { data: currentUser } = useCurrentUser();
  const reserveItem = useReserveItem();
  
  const getStatusColor = (status: ItemStatus) => {
    switch (status) {
      case 'AVAILABLE': return 'success';
      case 'RESERVED': return 'warning';
      case 'RENTED': return 'error';
      default: return 'default';
    }
  };
  
  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" gutterBottom>
          {item.name}
        </Typography>
        
        <Chip
          label={getStatusLabel(item.status)}
          color={getStatusColor(item.status)}
          size="small"
          sx={{ mb: 1 }}
        />
        
        <Typography variant="body2" color="text.secondary">
          {item.description}
        </Typography>
        
        {item.metadata && (
          <Box sx={{ mt: 1 }}>
            {/* 메타데이터 표시 */}
          </Box>
        )}
      </CardContent>
      
      <CardActions>
        {item.status === 'AVAILABLE' && onReserve && (
          <Button
            size="small"
            variant="contained"
            onClick={() => onReserve(item.id)}
            disabled={reserveItem.isLoading}
          >
            예약하기
          </Button>
        )}
        
        {showAdminActions && (
          <AdminItemActions item={item} />
        )}
      </CardActions>
    </Card>
  );
};
```

### 2. ReservationTimer 컴포넌트

```typescript
// src/features/reservations/components/ReservationTimer.tsx
interface ReservationTimerProps {
  expiresAt: string;
  onExpire?: () => void;
}

export const ReservationTimer: React.FC<ReservationTimerProps> = ({
  expiresAt,
  onExpire
}) => {
  const [timeLeft, setTimeLeft] = useState<number>(0);
  
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
  
  const formatTime = (milliseconds: number) => {
    const minutes = Math.floor(milliseconds / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };
  
  const getTimerColor = () => {
    if (timeLeft > 30 * 60 * 1000) return 'success'; // 30분 초과
    if (timeLeft > 10 * 60 * 1000) return 'warning'; // 10분 초과
    return 'error'; // 10분 이하
  };
  
  return (
    <Chip
      label={`남은 시간: ${formatTime(timeLeft)}`}
      color={getTimerColor()}
      size="small"
      icon={<AccessTimeIcon />}
    />
  );
};
```

---

## 🔄 API 통합 패턴

### 커스텀 훅 패턴

```typescript
// src/features/items/hooks/useItems.ts
export const useItems = (filters?: ItemFilters) => {
  return useQuery({
    queryKey: ['items', filters],
    queryFn: () => itemsAPI.getItems(filters),
    staleTime: 30 * 1000, // 30초간 캐시 유지
    refetchOnWindowFocus: true,
  });
};

export const useReserveItem = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: reservationsAPI.createReservation,
    onSuccess: () => {
      // 관련 캐시 무효화
      queryClient.invalidateQueries(['items']);
      queryClient.invalidateQueries(['reservations']);
    },
    onError: (error) => {
      toast.error(error.message || '예약에 실패했습니다.');
    }
  });
};
```

### API 클라이언트 설정

```typescript
// src/shared/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL + '/api/v1',
      timeout: 10000,
    });
    
    // 요청 인터셉터: JWT 토큰 추가
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // 응답 인터셉터: 에러 처리
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
  
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }
  
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }
  
  // PUT, DELETE 메서드들...
}

export const apiClient = new APIClient();
```

---

## 🎯 상태 관리 전략

### 1. Global State (React Context)
```typescript
// src/shared/contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children
}) => {
  const [user, setUser] = useState<User | null>(null);
  
  // Context value 및 provider 로직...
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 2. Server State (TanStack Query)
```typescript
// src/shared/hooks/useServerState.ts
export const useServerState = () => {
  const queryClient = useQueryClient();
  
  // 실시간 업데이트를 위한 폴링 설정
  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries(['items']);
      queryClient.invalidateQueries(['reservations', 'active']);
    }, 30000); // 30초마다 새로고침
    
    return () => clearInterval(interval);
  }, [queryClient]);
};
```

---

## 🌐 다국어 및 한국어 최적화

### Material-UI 테마 설정

```typescript
// src/shared/theme/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // 대학교 블루 컬러
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      '"Noto Sans KR"',
      '"Apple SD Gothic Neo"',
      '"Malgun Gothic"',
      'sans-serif'
    ].join(','),
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    body1: {
      lineHeight: 1.7, // 한글 가독성을 위한 줄 간격
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none', // 한국어에 대문자 변환 비활성화
        },
      },
    },
  },
});
```

---

## 📱 반응형 디자인

### 브레이크포인트 전략

```typescript
// src/shared/hooks/useResponsive.ts
export const useResponsive = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  
  return { isMobile, isTablet, isDesktop };
};
```

### 모바일 우선 레이아웃

```typescript
// src/shared/components/DashboardLayout.tsx
export const DashboardLayout: React.FC = () => {
  const { isMobile } = useResponsive();
  const [mobileOpen, setMobileOpen] = useState(false);
  
  return (
    <Box sx={{ display: 'flex' }}>
      {/* 모바일: Drawer, 데스크탑: 고정 사이드바 */}
      {isMobile ? (
        <SwipeableDrawer
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          onOpen={() => setMobileOpen(true)}
        >
          <NavigationMenu />
        </SwipeableDrawer>
      ) : (
        <Drawer variant="permanent">
          <NavigationMenu />
        </Drawer>
      )}
      
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Outlet />
      </Box>
    </Box>
  );
};
```

---

## 🔧 개발 환경 설정

### 환경 변수 (.env)

```bash
# API 설정
VITE_API_URL=http://localhost:8000

# 앱 설정
VITE_APP_TITLE=융합공과대학 렌탈 시스템
VITE_APP_VERSION=1.0.0

# 개발 모드 설정
VITE_DEV_MODE=true
```

### 패키지 설치 명령어

```bash
# 필수 의존성
npm install react@18 react-dom@18
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install @tanstack/react-query
npm install react-router-dom
npm install react-hook-form @hookform/resolvers yup
npm install axios
npm install dayjs

# 개발 의존성
npm install -D @types/react @types/react-dom
npm install -D @vitejs/plugin-react
npm install -D eslint @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier
```

---

## 🧪 테스트 전략

### 컴포넌트 테스트 예제

```typescript
// src/features/items/components/__tests__/ItemCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ItemCard } from '../ItemCard';
import { mockItem } from '../../__mocks__/items';

describe('ItemCard', () => {
  it('available 상태일 때 예약 버튼이 표시된다', () => {
    const mockOnReserve = jest.fn();
    
    render(
      <ItemCard 
        item={{ ...mockItem, status: 'AVAILABLE' }}
        onReserve={mockOnReserve}
      />
    );
    
    const reserveButton = screen.getByText('예약하기');
    expect(reserveButton).toBeInTheDocument();
    
    fireEvent.click(reserveButton);
    expect(mockOnReserve).toHaveBeenCalledWith(mockItem.id);
  });
});
```

---

## 🚀 성능 최적화

### 코드 분할 및 지연 로딩

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

// 라우트 기반 코드 분할
const AdminRoutes = lazy(() => import('./features/admin/AdminRoutes'));
const ItemsPage = lazy(() => import('./features/items/pages/ItemsPage'));

const App = () => (
  <Suspense fallback={<LoadingSpinner />}>
    <Router>
      <Routes>
        {/* 라우트 설정 */}
      </Routes>
    </Router>
  </Suspense>
);
```

### 이미지 최적화

```typescript
// src/shared/components/OptimizedImage.tsx
interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  return (
    <Box sx={{ position: 'relative', width, height }}>
      {loading && <Skeleton variant="rectangular" width={width} height={height} />}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoading(false)}
        onError={() => {
          setLoading(false);
          setError(true);
        }}
        style={{
          display: loading ? 'none' : 'block',
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
      />
      {error && <Box>이미지를 불러올 수 없습니다</Box>}
    </Box>
  );
};
```

---

## 📚 다음 단계

1. **샘플 데이터 생성**: 개발 및 테스트용 더미 데이터
2. **API 통합 테스트**: 백엔드와의 연동 테스트
3. **사용자 테스트**: 실제 학생들을 대상으로 한 UX 테스트
4. **성능 최적화**: 번들 크기 최적화 및 로딩 속도 개선
5. **PWA 기능 추가**: 모바일 앱과 같은 경험 제공

---

## 📞 문의 및 지원

개발 중 궁금한 사항이나 기술적 문제가 있다면 언제든 문의해 주세요.

**백엔드 API 문서**: `http://localhost:8000/docs`  
**개발 서버 실행**: 백엔드가 포트 8000에서 실행 중이므로 프론트엔드는 포트 3000 사용 권장