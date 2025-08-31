# UI 설계 및 화면 구조 가이드

## 📋 개요 (2025-08-30 업데이트)

융합공과대학 렌탈 관리 시스템의 사용자 인터페이스 설계 가이드입니다.

**설계 원칙**: 모바일 우선, 직관적 UI, 한국어 최적화, 3클릭 룰

⚠️ **현재 상태**: 
- Vite + pnpm 개발환경으로 완전 마이그레이션 완료
- Material-UI v5 + TypeScript 5.3.3 기반
- 인증 시스템 안정화 (Redis 없이도 정상 작동)
- Toast 알림 시스템 구현 완료

---

## 🎨 디자인 시스템

### 컬러 팔레트

```css
/* 메인 컬러 */
--primary: #1976d2;          /* 대학교 블루 */
--primary-light: #42a5f5;
--primary-dark: #1565c0;

/* 상태 컬러 */
--success: #4caf50;          /* 대여가능 (초록) */
--warning: #ff9800;          /* 예약됨 (주황) */
--error: #f44336;            /* 대여중/연체 (빨강) */
--info: #2196f3;             /* 정보 (파랑) */

/* 중성 컬러 */
--grey-50: #fafafa;
--grey-100: #f5f5f5;
--grey-300: #e0e0e0;
--grey-500: #9e9e9e;
--grey-700: #616161;
--grey-900: #212121;

/* 텍스트 */
--text-primary: #212121;
--text-secondary: #757575;
--text-disabled: #bdbdbd;
```

### 타이포그래피

```css
/* 한국어 최적화 폰트 스택 */
font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;

/* 크기 스케일 */
--text-xs: 12px;     /* 보조 텍스트 */
--text-sm: 14px;     /* 본문 */
--text-base: 16px;   /* 기본 */
--text-lg: 18px;     /* 소제목 */
--text-xl: 20px;     /* 제목 */
--text-2xl: 24px;    /* 대제목 */
--text-3xl: 30px;    /* 페이지 제목 */

/* 줄 간격 (한글 가독성) */
--line-height-tight: 1.4;
--line-height-normal: 1.6;
--line-height-loose: 1.8;
```

### 간격 시스템

```css
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;
--spacing-3xl: 64px;
```

---

## 📱 반응형 브레이크포인트

```css
/* Mobile First 접근 */
@media (min-width: 576px) { /* 큰 모바일 */ }
@media (min-width: 768px) { /* 태블릿 */ }
@media (min-width: 992px) { /* 데스크탑 */ }
@media (min-width: 1200px) { /* 대형 데스크탑 */ }
```

---

## 🗂️ 페이지 구조 및 화면 설계

### 1. 로그인 페이지 (`/login`)

#### 와이어프레임
```
┌─────────────────────────────────────┐
│               로고/제목              │
│        융합공과대학 렌탈 시스템       │
├─────────────────────────────────────┤
│                                     │
│         ┌─────────────────┐        │
│  학번   │                 │        │
│         └─────────────────┘        │
│                                     │
│         ┌─────────────────┐        │
│  비밀번호│                 │        │
│         └─────────────────┘        │
│                                     │
│         ┌─────────────────┐        │
│         │    로그인 하기    │        │
│         └─────────────────┘        │
│                                     │
│         대학교 시스템으로 인증합니다   │
│                                     │
└─────────────────────────────────────┘
```

#### 컴포넌트 구조 (수정됨)
```typescript
// LoginPage.tsx - ⚠️ 현재 Toast 알림 시스템 적용됨
<Container maxWidth="sm">
  <Box sx={{ mt: 8, mb: 4, textAlign: 'center' }}>
    <Typography variant="h3" component="h1" gutterBottom>
      융합공과대학 렌탈 시스템
    </Typography>
    <Typography variant="body1" color="text.secondary">
      학생증으로 간편하게 대여하세요
    </Typography>
  </Box>
  
  <LoginForm onSuccess={() => showToast('로그인 성공!')} />
  
  <Box sx={{ mt: 3, textAlign: 'center' }}>
    <Typography variant="body2" color="text.secondary">
      대학교 홈페이지 계정으로 로그인합니다
    </Typography>
  </Box>
  
  {/* Toast 컨테이너 추가됨 */}
  <ToastContainer />
</Container>
```

### 2. 메인 대시보드 (`/`)

#### 와이어프레임 (모바일)
```
┌─────────────────────────────────────┐
│ ☰  융공대 렌탈 시스템    👤 사용자   │
├─────────────────────────────────────┤
│                                     │
│  📊 내 현황                          │
│  ├ 활성 예약: 1개 (45분 남음) ⏰     │
│  ├ 활성 대여: 2개                    │
│  └ 연체: 0개                        │
│                                     │
│  🔍 품목 검색                        │
│  ┌─────────────────┐  [필터] [정렬] │
│  │ 검색어 입력...   │               │
│  └─────────────────┘               │
│                                     │
│  📂 카테고리                         │
│  [운동용품] [전자기기] [생활용품]     │
│  [엔터테인먼트] [학업용품] [더보기]   │
│                                     │
│  📦 대여 가능한 품목                 │
│  ┌─────────────────┐               │
│  │ 🏀 농구공        │   [예약하기]   │
│  │ 나이키 5호       │               │
│  │ 🟢 대여가능      │               │
│  └─────────────────┘               │
│                                     │
└─────────────────────────────────────┘
```

#### 컴포넌트 구조
```typescript
// DashboardPage.tsx
<DashboardLayout>
  <Container maxWidth="lg">
    {/* 사용자 현황 카드 */}
    <UserStatusCard />
    
    {/* 검색 및 필터 */}
    <SearchAndFilter />
    
    {/* 카테고리 필터 */}
    <CategoryFilter />
    
    {/* 품목 그리드 */}
    <ItemsGrid />
  </Container>
</DashboardLayout>
```

### 3. 품목 상세 페이지 (`/items/:id`)

#### 와이어프레임
```
┌─────────────────────────────────────┐
│ ← 뒤로가기                           │
├─────────────────────────────────────┤
│                                     │
│         ┌─────────────┐             │
│         │             │             │
│         │   품목 이미지  │             │
│         │             │             │
│         └─────────────┘             │
│                                     │
│  🏀 농구공                           │
│  🟢 대여 가능 상태                    │
│                                     │
│  일련번호: SPORT-002                │
│  카테고리: 운동용품                   │
│  브랜드: 스팰딩                      │
│  크기: 7호                          │
│                                     │
│  설명: 농구 경기 및 연습용 공식 농구공 │
│                                     │
│         ┌─────────────────┐        │
│         │    예약 하기     │        │
│         └─────────────────┘        │
│                                     │
└─────────────────────────────────────┘
```

#### 컴포넌트 구조
```typescript
// ItemDetailPage.tsx
<Container maxWidth="md">
  <Box sx={{ mb: 2 }}>
    <IconButton onClick={handleGoBack}>
      <ArrowBackIcon />
    </IconButton>
    <Typography variant="body2" component="span" sx={{ ml: 1 }}>
      뒤로가기
    </Typography>
  </Box>
  
  <ItemDetailCard item={item} />
  <ItemMetadata metadata={item.item_metadata} />
  <ItemActions item={item} onReserve={handleReserve} />
</Container>
```

### 4. 내 예약 페이지 (`/my-reservations`)

#### 와이어프레임
```
┌─────────────────────────────────────┐
│  내 예약 현황                        │
├─────────────────────────────────────┤
│                                     │
│  활성 예약 (1)                       │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 📱 보조배터리 (ELEC-001)        │ │
│  │ 예약일시: 2025-08-30 12:45      │ │
│  │ 만료까지: ⏰ 45분 13초 남음      │ │
│  │                  [취소] [연장]  │ │
│  └─────────────────────────────────┘ │
│                                     │
│  최근 예약 (5)                       │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🏀 농구공 (SPORT-002)           │ │
│  │ 예약일: 2025-08-29              │ │
│  │ 상태: ✅ 완료 (수령함)          │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🎯 다트게임 (GAME-004)          │ │
│  │ 예약일: 2025-08-28              │ │
│  │ 상태: ❌ 만료됨                 │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

#### 핵심 컴포넌트: 예약 타이머

```typescript
// ReservationTimerCard.tsx
interface ReservationTimerCardProps {
  reservation: Reservation;
  onCancel: (id: number) => void;
  onExtend?: (id: number) => void;
}

export const ReservationTimerCard: React.FC<ReservationTimerCardProps> = ({
  reservation,
  onCancel,
  onExtend
}) => {
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [isUrgent, setIsUrgent] = useState(false);
  
  useEffect(() => {
    const updateTimer = () => {
      const now = new Date().getTime();
      const expiry = new Date(reservation.expires_at).getTime();
      const difference = expiry - now;
      
      if (difference > 0) {
        setTimeLeft(difference);
        setIsUrgent(difference < 10 * 60 * 1000); // 10분 미만
      } else {
        setTimeLeft(0);
        setIsUrgent(true);
      }
    };
    
    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    
    return () => clearInterval(interval);
  }, [reservation.expires_at]);
  
  const formatTime = (milliseconds: number) => {
    const minutes = Math.floor(milliseconds / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    return `${minutes}분 ${seconds}초`;
  };
  
  return (
    <Card sx={{ 
      mb: 2,
      border: isUrgent ? '2px solid #f44336' : '1px solid #e0e0e0',
      bgcolor: isUrgent ? '#ffebee' : 'white'
    }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="start">
          <Box>
            <Typography variant="h6">{reservation.item.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {reservation.item.serial_number}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              예약일시: {format(new Date(reservation.reserved_at), 'MM/dd HH:mm')}
            </Typography>
          </Box>
          
          <Box textAlign="right">
            {timeLeft > 0 ? (
              <Chip
                label={`⏰ ${formatTime(timeLeft)} 남음`}
                color={isUrgent ? 'error' : 'success'}
                size="small"
              />
            ) : (
              <Chip label="⏰ 만료됨" color="error" size="small" />
            )}
          </Box>
        </Box>
        
        {isUrgent && (
          <Alert severity="warning" sx={{ mt: 2, mb: 1 }}>
            {timeLeft > 0 
              ? '곧 예약이 만료됩니다! 서둘러 수령해 주세요.' 
              : '예약이 만료되었습니다. 다시 예약해 주세요.'}
          </Alert>
        )}
        
        <Box display="flex" gap={1} mt={2}>
          <Button
            size="small"
            variant="outlined"
            color="error"
            onClick={() => onCancel(reservation.id)}
            disabled={timeLeft === 0}
          >
            취소
          </Button>
          
          {onExtend && timeLeft > 0 && (
            <Button
              size="small"
              variant="outlined"
              onClick={() => onExtend(reservation.id)}
            >
              연장 요청
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
```

### 5. 내 대여 페이지 (`/my-rentals`)

#### 와이어프레임
```
┌─────────────────────────────────────┐
│  내 대여 현황                        │
├─────────────────────────────────────┤
│                                     │
│  활성 대여 (2)                       │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🏸 배드민턴 라켓 (SPORT-003)    │ │
│  │ 대여일: 2025-08-23              │ │
│  │ 반납예정: 2025-08-30 (오늘)     │ │
│  │ 상태: 🟡 반납 예정              │ │
│  └─────────────────────────────────┘ │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ 🎲 카탄 (GAME-002)              │ │
│  │ 대여일: 2025-08-22              │ │
│  │ 반납예정: 2025-08-29 (어제)     │ │
│  │ 상태: 🔴 연체 1일               │ │
│  └─────────────────────────────────┘ │
│                                     │
│  대여 이력 (10)                      │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │ ⚽ 축구공 (SPORT-001)           │ │
│  │ 대여: 08/15 ~ 08/22             │ │
│  │ 상태: ✅ 반납 완료               │ │
│  └─────────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### 6. 관리자 대시보드 (`/admin`)

#### 와이어프레임 (데스크톱)
```
┌─────────────────────────────────────────────────────────────┐
│  관리자 대시보드                           👤 관리자  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 실시간 현황                                              │
│  ┌──────────┬──────────┬──────────┬──────────┐              │
│  │ 활성 예약 │ 활성 대여 │ 연체 건수 │ 대여가능  │              │
│  │    3     │    12    │    2     │    45    │              │
│  └──────────┴──────────┴──────────┴──────────┘              │
│                                                             │
│  🚨 긴급 처리 필요                                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 예약 만료 임박 (5분 이내)                               │ │
│  │ • 보조배터리 (ELEC-001) - 사용자1 (2분 남음)            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 연체된 대여                                             │ │
│  │ • 카탄 (GAME-002) - 사용자2 (1일 연체)                  │ │
│  │ • 캠핑의자 (CAMP-003) - 사용자3 (3일 연체)              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  📈 통계 차트                                               │
│  [일별 대여량] [인기 품목] [카테고리별 현황] [사용자 활동]   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7. 품목 관리 페이지 (`/admin/items`)

#### 와이어프레임
```
┌─────────────────────────────────────────────────────────────┐
│  품목 관리                                    [+ 새 품목 추가] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔍 검색 및 필터                                             │
│  ┌──────────────┐ [카테고리▼] [상태▼] [정렬▼] [검색]       │
│  │ 검색어...    │                                          │
│  └──────────────┘                                          │
│                                                             │
│  📊 품목 현황: 총 22개 (대여가능 15 | 예약됨 1 | 대여중 4 | 점검중 2) │
│                                                             │
│  품목 목록                                                   │
│  ┌─────┬──────────┬────────┬────────┬──────┬──────┐        │
│  │ 상태│   이름    │ 일련번호│ 카테고리│ 위치  │ 작업  │        │
│  ├─────┼──────────┼────────┼────────┼──────┼──────┤        │
│  │ 🟢  │ 축구공    │SPORT-001│운동용품│ A-01 │[편집] │        │
│  │ 🟡  │보조배터리 │ELEC-001 │전자기기│ B-05 │[편집] │        │
│  │ 🔴  │배드민턴라켓│SPORT-003│운동용품│ A-03 │[편집] │        │
│  │ 🟢  │ 농구공    │SPORT-002│운동용품│ A-02 │[편집] │        │
│  └─────┴──────────┴────────┴────────┴──────┴──────┘        │
│                                                             │
│                                      [이전] 1/3 [다음]      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 핵심 컴포넌트 설계

### 1. ItemCard 컴포넌트

```typescript
// ItemCard.tsx
interface ItemCardProps {
  item: Item;
  variant?: 'student' | 'admin';
  onReserve?: (itemId: number) => void;
  onEdit?: (itemId: number) => void;
  onStatusChange?: (itemId: number, status: ItemStatus) => void;
}

export const ItemCard: React.FC<ItemCardProps> = ({
  item,
  variant = 'student',
  onReserve,
  onEdit,
  onStatusChange
}) => {
  const getStatusConfig = (status: ItemStatus) => {
    switch (status) {
      case 'AVAILABLE':
        return { color: '#4caf50', icon: '🟢', label: '대여가능' };
      case 'RESERVED':
        return { color: '#ff9800', icon: '🟡', label: '예약됨' };
      case 'RENTED':
        return { color: '#f44336', icon: '🔴', label: '대여중' };
      case 'MAINTENANCE':
        return { color: '#9e9e9e', icon: '🔧', label: '점검중' };
    }
  };
  
  const statusConfig = getStatusConfig(item.status);
  
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        '&:hover': { boxShadow: 3 }
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
          <Typography variant="h6" component="h3">
            {item.name}
          </Typography>
          
          <Chip
            label={`${statusConfig.icon} ${statusConfig.label}`}
            size="small"
            sx={{ 
              bgcolor: statusConfig.color + '20',
              color: statusConfig.color,
              fontWeight: 'bold'
            }}
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {item.serial_number} • {item.category.name}
        </Typography>
        
        <Typography variant="body2" paragraph>
          {item.description}
        </Typography>
        
        {item.item_metadata && (
          <ItemMetadataChips metadata={item.item_metadata} />
        )}
      </CardContent>
      
      <CardActions>
        {variant === 'student' && item.status === 'AVAILABLE' && onReserve && (
          <Button
            size="small"
            variant="contained"
            onClick={() => onReserve(item.id)}
            fullWidth
          >
            예약하기
          </Button>
        )}
        
        {variant === 'admin' && (
          <Box display="flex" gap={1} width="100%">
            <Button
              size="small"
              variant="outlined"
              onClick={() => onEdit?.(item.id)}
            >
              편집
            </Button>
            
            <StatusChangeMenu
              currentStatus={item.status}
              onStatusChange={(newStatus) => onStatusChange?.(item.id, newStatus)}
            />
          </Box>
        )}
      </CardActions>
    </Card>
  );
};
```

### 2. NavigationDrawer 컴포넌트

```typescript
// NavigationDrawer.tsx
interface NavigationDrawerProps {
  open: boolean;
  onClose: () => void;
  user: User;
}

export const NavigationDrawer: React.FC<NavigationDrawerProps> = ({
  open,
  onClose,
  user
}) => {
  const navigate = useNavigate();
  
  const studentMenuItems = [
    { icon: <HomeIcon />, label: '메인 화면', path: '/' },
    { icon: <BookmarkIcon />, label: '내 예약', path: '/my-reservations' },
    { icon: <AssignmentIcon />, label: '내 대여', path: '/my-rentals' },
  ];
  
  const adminMenuItems = [
    ...studentMenuItems,
    { divider: true },
    { icon: <AdminPanelSettingsIcon />, label: '관리자 대시보드', path: '/admin' },
    { icon: <InventoryIcon />, label: '품목 관리', path: '/admin/items' },
    { icon: <CategoryIcon />, label: '카테고리 관리', path: '/admin/categories' },
    { icon: <BookmarkBorderIcon />, label: '예약 관리', path: '/admin/reservations' },
    { icon: <AssignmentTurnedInIcon />, label: '대여 관리', path: '/admin/rentals' },
    { icon: <BarChartIcon />, label: '통계', path: '/admin/statistics' },
  ];
  
  const menuItems = user.role === 'ADMIN' ? adminMenuItems : studentMenuItems;
  
  return (
    <Drawer anchor="left" open={open} onClose={onClose}>
      <Box sx={{ width: 280 }}>
        {/* 사용자 프로필 헤더 */}
        <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="subtitle1" fontWeight="bold">
            {user.name}
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {user.student_id} • {user.department}
          </Typography>
          <Chip
            label={user.role === 'ADMIN' ? '관리자' : '학생'}
            size="small"
            sx={{ 
              mt: 1, 
              bgcolor: 'rgba(255,255,255,0.2)',
              color: 'white'
            }}
          />
        </Box>
        
        {/* 메뉴 목록 */}
        <List>
          {menuItems.map((item, index) => (
            item.divider ? (
              <Divider key={`divider-${index}`} sx={{ my: 1 }} />
            ) : (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  onClick={() => {
                    navigate(item.path);
                    onClose();
                  }}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            )
          ))}
          
          <Divider sx={{ my: 1 }} />
          
          <ListItem disablePadding>
            <ListItemButton onClick={handleLogout}>
              <ListItemIcon><ExitToAppIcon /></ListItemIcon>
              <ListItemText primary="로그아웃" />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
};
```

### 3. SearchAndFilter 컴포넌트

```typescript
// SearchAndFilter.tsx
interface SearchAndFilterProps {
  onSearch: (query: string) => void;
  onCategoryChange: (categoryId: number | null) => void;
  onStatusChange: (status: ItemStatus | null) => void;
  categories: Category[];
}

export const SearchAndFilter: React.FC<SearchAndFilterProps> = ({
  onSearch,
  onCategoryChange,
  onStatusChange,
  categories
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<ItemStatus | null>(null);
  
  const handleSearchChange = useDebouncedCallback((value: string) => {
    onSearch(value);
  }, 300);
  
  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
        {/* 검색창 */}
        <TextField
          placeholder="품목명, 일련번호로 검색..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            handleSearchChange(e.target.value);
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1, minWidth: 200 }}
        />
        
        {/* 카테고리 필터 */}
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>카테고리</InputLabel>
          <Select
            value={selectedCategory || ''}
            onChange={(e) => {
              const value = e.target.value as number;
              setSelectedCategory(value || null);
              onCategoryChange(value || null);
            }}
          >
            <MenuItem value="">전체</MenuItem>
            {categories.map(category => (
              <MenuItem key={category.id} value={category.id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        {/* 상태 필터 */}
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>상태</InputLabel>
          <Select
            value={selectedStatus || ''}
            onChange={(e) => {
              const value = e.target.value as ItemStatus;
              setSelectedStatus(value || null);
              onStatusChange(value || null);
            }}
          >
            <MenuItem value="">전체</MenuItem>
            <MenuItem value="AVAILABLE">🟢 대여가능</MenuItem>
            <MenuItem value="RESERVED">🟡 예약됨</MenuItem>
            <MenuItem value="RENTED">🔴 대여중</MenuItem>
            <MenuItem value="MAINTENANCE">🔧 점검중</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Paper>
  );
};
```

---

## 📱 모바일 최적화 가이드

### 1. 터치 친화적 UI

```css
/* 최소 터치 영역 44px */
.touch-target {
  min-height: 44px;
  min-width: 44px;
}

/* 스와이프 제스처 지원 */
.swipeable-card {
  position: relative;
  overflow: hidden;
}

/* 풀 스크린 모달 (모바일) */
@media (max-width: 768px) {
  .modal {
    width: 100%;
    height: 100%;
    margin: 0;
    border-radius: 0;
  }
}
```

### 2. 모바일 네비게이션 패턴

```typescript
// MobileBottomNavigation.tsx (옵션)
export const MobileBottomNavigation: React.FC = () => {
  const [value, setValue] = useState(0);
  const navigate = useNavigate();
  
  return (
    <Paper 
      sx={{ 
        position: 'fixed', 
        bottom: 0, 
        left: 0, 
        right: 0,
        display: { xs: 'block', md: 'none' } // 모바일에서만 표시
      }}
    >
      <BottomNavigation
        value={value}
        onChange={(event, newValue) => {
          setValue(newValue);
          // 네비게이션 로직
        }}
      >
        <BottomNavigationAction 
          label="홈" 
          icon={<HomeIcon />} 
        />
        <BottomNavigationAction 
          label="예약" 
          icon={<BookmarkIcon />} 
        />
        <BottomNavigationAction 
          label="대여" 
          icon={<AssignmentIcon />} 
        />
        <BottomNavigationAction 
          label="더보기" 
          icon={<MoreIcon />} 
        />
      </BottomNavigation>
    </Paper>
  );
};
```

### 3. 스와이프 동작

```typescript
// SwipeableItemCard.tsx
import { useSwipeable } from 'react-swipeable';

export const SwipeableItemCard: React.FC<{ item: Item }> = ({ item }) => {
  const handlers = useSwipeable({
    onSwipedLeft: () => {
      // 왼쪽 스와이프: 예약하기
      if (item.status === 'AVAILABLE') {
        handleReserve(item.id);
      }
    },
    onSwipedRight: () => {
      // 오른쪽 스와이프: 상세보기
      navigate(`/items/${item.id}`);
    },
    trackMouse: true
  });
  
  return (
    <div {...handlers}>
      <ItemCard item={item} />
      
      {/* 스와이프 힌트 */}
      <Box sx={{ 
        position: 'absolute', 
        bottom: 8, 
        right: 8, 
        opacity: 0.6,
        display: { xs: 'block', md: 'none' }
      }}>
        <Typography variant="caption">
          ← 예약 | 상세 →
        </Typography>
      </Box>
    </div>
  );
};
```

---

## ⚡ 성능 최적화 가이드

### 1. 이미지 최적화

```typescript
// LazyImage.tsx
interface LazyImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
}

export const LazyImage: React.FC<LazyImageProps> = ({ 
  src, 
  alt, 
  width = 200, 
  height = 200 
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  return (
    <Box 
      sx={{ 
        position: 'relative', 
        width, 
        height, 
        bgcolor: 'grey.100',
        borderRadius: 1
      }}
    >
      {loading && (
        <Skeleton 
          variant="rectangular" 
          width={width} 
          height={height}
          sx={{ position: 'absolute', top: 0, left: 0 }}
        />
      )}
      
      {!error && (
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
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            borderRadius: '4px',
            display: loading ? 'none' : 'block'
          }}
        />
      )}
      
      {error && (
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          width="100%"
          height="100%"
          bgcolor="grey.200"
          color="grey.500"
        >
          <ImageNotSupportedIcon />
        </Box>
      )}
    </Box>
  );
};
```

### 2. 가상화 (대량 데이터)

```typescript
// VirtualizedItemList.tsx
import { FixedSizeList as List } from 'react-window';

interface VirtualizedItemListProps {
  items: Item[];
  onItemClick: (item: Item) => void;
}

export const VirtualizedItemList: React.FC<VirtualizedItemListProps> = ({
  items,
  onItemClick
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <ItemCard 
        item={items[index]} 
        onClick={() => onItemClick(items[index])} 
      />
    </div>
  );
  
  return (
    <List
      height={600}
      itemCount={items.length}
      itemSize={200}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

---

## 🎯 사용자 경험 (UX) 가이드라인

### 1. 로딩 상태 관리

```typescript
// LoadingStates.tsx
export const ItemsLoadingGrid: React.FC = () => (
  <Grid container spacing={2}>
    {Array.from(new Array(6)).map((_, index) => (
      <Grid item xs={12} sm={6} md={4} key={index}>
        <Card>
          <Skeleton variant="rectangular" height={140} />
          <CardContent>
            <Skeleton variant="text" height={32} />
            <Skeleton variant="text" height={20} width="60%" />
            <Skeleton variant="text" height={16} />
          </CardContent>
          <CardActions>
            <Skeleton variant="rectangular" height={36} width={100} />
          </CardActions>
        </Card>
      </Grid>
    ))}
  </Grid>
);
```

### 2. 에러 상태 처리

```typescript
// ErrorBoundary.tsx
interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    minHeight="400px"
    textAlign="center"
    p={3}
  >
    <ErrorOutlineIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
    
    <Typography variant="h5" gutterBottom>
      문제가 발생했습니다
    </Typography>
    
    <Typography variant="body1" color="text.secondary" paragraph>
      {error.message || '알 수 없는 오류가 발생했습니다.'}
    </Typography>
    
    <Button
      variant="contained"
      onClick={resetError}
      startIcon={<RefreshIcon />}
    >
      다시 시도
    </Button>
  </Box>
);
```

### 3. 피드백 시스템

```typescript
// ToastProvider.tsx
export const useToast = () => {
  const showSuccess = (message: string, options?: SnackbarProps) => {
    enqueueSnackbar(message, {
      variant: 'success',
      autoHideDuration: 3000,
      anchorOrigin: { horizontal: 'center', vertical: 'bottom' },
      ...options
    });
  };
  
  const showError = (message: string, options?: SnackbarProps) => {
    enqueueSnackbar(message, {
      variant: 'error',
      autoHideDuration: 5000,
      anchorOrigin: { horizontal: 'center', vertical: 'top' },
      ...options
    });
  };
  
  const showWarning = (message: string, options?: SnackbarProps) => {
    enqueueSnackbar(message, {
      variant: 'warning',
      autoHideDuration: 4000,
      ...options
    });
  };
  
  return { showSuccess, showError, showWarning };
};
```

---

## 🧪 테스트 가능한 UI 패턴

### 1. 테스트 친화적 컴포넌트

```typescript
// ItemCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ItemCard } from './ItemCard';

describe('ItemCard', () => {
  const mockItem: Item = {
    id: 1,
    name: '테스트 품목',
    status: 'AVAILABLE',
    serial_number: 'TEST-001',
    category: { name: '테스트 카테고리' }
  };
  
  it('대여 가능한 품목에 예약 버튼이 표시된다', () => {
    const mockOnReserve = jest.fn();
    
    render(
      <ItemCard 
        item={mockItem} 
        onReserve={mockOnReserve}
        data-testid="item-card"
      />
    );
    
    expect(screen.getByText('테스트 품목')).toBeInTheDocument();
    expect(screen.getByText('🟢 대여가능')).toBeInTheDocument();
    
    const reserveButton = screen.getByRole('button', { name: '예약하기' });
    fireEvent.click(reserveButton);
    
    expect(mockOnReserve).toHaveBeenCalledWith(1);
  });
});
```

### 2. 접근성 (A11y) 고려사항

```typescript
// AccessibleItemCard.tsx
export const AccessibleItemCard: React.FC<ItemCardProps> = ({ item, onReserve }) => {
  const statusLabels = {
    AVAILABLE: '대여 가능',
    RESERVED: '예약됨',
    RENTED: '대여중',
    MAINTENANCE: '점검중'
  };
  
  return (
    <Card 
      role="article"
      aria-label={`${item.name} 품목 정보`}
      tabIndex={0}
    >
      <CardContent>
        <Typography 
          variant="h6" 
          component="h3"
          id={`item-title-${item.id}`}
        >
          {item.name}
        </Typography>
        
        <Box
          role="status"
          aria-label={`현재 상태: ${statusLabels[item.status]}`}
        >
          <Chip label={`🟢 ${statusLabels[item.status]}`} />
        </Box>
        
        <Typography
          variant="body2"
          aria-describedby={`item-title-${item.id}`}
        >
          {item.description}
        </Typography>
      </CardContent>
      
      <CardActions>
        {item.status === 'AVAILABLE' && (
          <Button
            onClick={() => onReserve?.(item.id)}
            aria-label={`${item.name} 예약하기`}
          >
            예약하기
          </Button>
        )}
      </CardActions>
    </Card>
  );
};
```

---

## 🚀 구현 우선순위

### Phase 1: 핵심 기능 (1주차)
1. ✅ 로그인 페이지
2. ✅ 메인 대시보드 (품목 목록)
3. ✅ 예약 기능
4. ✅ 내 예약 페이지

### Phase 2: 사용자 기능 완성 (2주차)
1. 🔄 품목 상세 페이지
2. 🔄 내 대여 페이지
3. 🔄 검색 및 필터링
4. 🔄 반응형 디자인

### Phase 3: 관리자 기능 (3주차)
1. 📋 관리자 대시보드
2. 📋 품목 관리
3. 📋 예약/대여 관리
4. 📋 통계 페이지

### Phase 4: 최적화 (4주차)
1. 📋 성능 최적화
2. 📋 접근성 개선
3. 📋 테스트 추가
4. 📋 PWA 기능

---

이 가이드를 참고하여 일관되고 사용하기 쉬운 인터페이스를 구현해 주세요. 궁금한 사항이나 추가 설명이 필요한 부분이 있다면 언제든 문의해 주세요!