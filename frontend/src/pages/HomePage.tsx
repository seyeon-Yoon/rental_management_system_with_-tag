import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  InputAdornment,
  Alert,
  Pagination,
  Skeleton,
} from '@mui/material';
import {
  Search,
  Category as CategoryIcon,
  CheckCircle,
  Schedule,
  Build,
  Block,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { itemService } from '../services/itemService';
import { categoryService } from '../services/categoryService';
import { reservationService } from '../services/reservationService';
import { Item, Category } from '../types';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const HomePage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | ''>('');
  const [page, setPage] = useState(1);
  const [reservationLoading, setReservationLoading] = useState<number | null>(null);
  const [reservationError, setReservationError] = useState<string | null>(null);
  const [reservationSuccess, setReservationSuccess] = useState<string | null>(null);

  const itemsPerPage = 12;

  // 카테고리 목록 조회
  const { data: categoriesResponse } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryService.getCategories({ limit: 100 }),
  });

  // 품목 목록 조회
  const {
    data: itemsResponse,
    isLoading: itemsLoading,
    error: itemsError,
    refetch: refetchItems,
  } = useQuery({
    queryKey: ['items', searchTerm, selectedCategory, page],
    queryFn: () => 
      itemService.getAvailableItems({
        page,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        category_id: selectedCategory || undefined,
      }),
  });

  // 내 활성 예약 조회 (중복 예약 방지용)
  const { data: myReservations, refetch: refetchReservations } = useQuery({
    queryKey: ['my-reservations'],
    queryFn: reservationService.getMyActiveReservations,
  });

  // 검색어 변경 시 페이지 리셋
  useEffect(() => {
    setPage(1);
  }, [searchTerm, selectedCategory]);

  // 성공/에러 메시지 자동 지우기
  useEffect(() => {
    if (reservationSuccess) {
      const timer = setTimeout(() => setReservationSuccess(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [reservationSuccess]);

  useEffect(() => {
    if (reservationError) {
      const timer = setTimeout(() => setReservationError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [reservationError]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return <CheckCircle color="success" />;
      case 'RESERVED':
        return <Schedule color="warning" />;
      case 'RENTED':
        return <Block color="error" />;
      case 'MAINTENANCE':
        return <Build color="info" />;
      default:
        return undefined;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return '대여 가능';
      case 'RESERVED':
        return '예약됨';
      case 'RENTED':
        return '대여 중';
      case 'MAINTENANCE':
        return '정비 중';
      default:
        return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE':
        return 'success';
      case 'RESERVED':
        return 'warning';
      case 'RENTED':
        return 'error';
      case 'MAINTENANCE':
        return 'info';
      default:
        return 'default';
    }
  };

  const handleReservation = async (item: Item) => {
    setReservationLoading(item.id);
    setReservationError(null);
    setReservationSuccess(null);

    try {
      await reservationService.createReservation({ item_id: item.id });
      setReservationSuccess(`${item.name} 예약이 완료되었습니다! 1시간 내에 학생회실로 오세요.`);
      
      // 데이터 새로고침
      await Promise.all([
        refetchItems(),
        refetchReservations(),
      ]);
    } catch (error: any) {
      console.error('예약 실패:', error);
      setReservationError(error.message || '예약에 실패했습니다.');
    } finally {
      setReservationLoading(null);
    }
  };

  const isItemAlreadyReserved = (itemId: number) => {
    return myReservations?.some(reservation => reservation.item_id === itemId);
  };

  const categories = categoriesResponse?.items || [];
  const items = itemsResponse?.items || [];
  const totalPages = Math.ceil((itemsResponse?.total || 0) / itemsPerPage);

  if (itemsLoading && page === 1) {
    return <Loading message="품목 목록을 불러오는 중..." fullHeight />;
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          대여 가능한 품목
        </Typography>
        <Typography variant="body1" color="text.secondary">
          원하는 품목을 찾아 예약하세요. 예약 후 1시간 내에 학생회실에서 수령 가능합니다.
        </Typography>
      </Box>

      {/* 알림 메시지 */}
      {reservationSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {reservationSuccess}
        </Alert>
      )}

      {reservationError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {reservationError}
        </Alert>
      )}

      {/* 검색 및 필터 */}
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="품목명으로 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>카테고리</InputLabel>
              <Select
                value={selectedCategory}
                label="카테고리"
                onChange={(e) => setSelectedCategory(e.target.value as number | '')}
                startAdornment={
                  <InputAdornment position="start">
                    <CategoryIcon />
                  </InputAdornment>
                }
              >
                <MenuItem value="">전체 카테고리</MenuItem>
                {categories.map((category: Category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* 에러 처리 */}
      {itemsError && (
        <ErrorMessage
          title="품목을 불러오는데 실패했습니다"
          message={itemsError.message}
          onRetry={() => refetchItems()}
        />
      )}

      {/* 품목 목록 */}
      {items.length === 0 && !itemsLoading ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            조건에 맞는 품목이 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            다른 검색 조건을 시도해보세요
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {itemsLoading && page > 1
            ? // 페이지네이션 로딩 시 스켈레톤 표시
              Array.from({ length: itemsPerPage }, (_, index) => (
                <Grid item xs={12} sm={6} md={4} key={`skeleton-${index}`}>
                  <Card>
                    <CardContent>
                      <Skeleton variant="text" width="60%" height={28} />
                      <Skeleton variant="text" width="40%" height={24} />
                      <Skeleton variant="rectangular" width="100%" height={20} sx={{ mt: 1 }} />
                    </CardContent>
                    <CardActions>
                      <Skeleton variant="rectangular" width={100} height={36} />
                    </CardActions>
                  </Card>
                </Grid>
              ))
            : items.map((item: Item) => (
                <Grid item xs={12} sm={6} md={4} key={item.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: 4,
                      },
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        {getStatusIcon(item.status)}
                        <Typography variant="h6" component="h3" sx={{ ml: 1 }}>
                          {item.name}
                        </Typography>
                      </Box>

                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {item.category?.name}
                      </Typography>

                      {item.description && (
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {item.description}
                        </Typography>
                      )}

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          일련번호:
                        </Typography>
                        <Typography variant="caption" fontFamily="monospace">
                          {item.serial_number}
                        </Typography>
                      </Box>

                      <Chip
                        label={getStatusText(item.status)}
                        color={getStatusColor(item.status) as any}
                        size="small"
                        icon={getStatusIcon(item.status)}
                      />
                    </CardContent>

                    <CardActions sx={{ p: 2, pt: 0 }}>
                      <Button
                        fullWidth
                        variant={item.status === 'AVAILABLE' ? 'contained' : 'outlined'}
                        disabled={
                          item.status !== 'AVAILABLE' || 
                          reservationLoading === item.id || 
                          isItemAlreadyReserved(item.id)
                        }
                        onClick={() => handleReservation(item)}
                      >
                        {reservationLoading === item.id
                          ? '예약 중...'
                          : isItemAlreadyReserved(item.id)
                          ? '이미 예약됨'
                          : item.status === 'AVAILABLE'
                          ? '예약하기'
                          : '예약 불가'}
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
        </Grid>
      )}

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
            size="large"
          />
        </Box>
      )}
    </Container>
  );
};

export default HomePage;