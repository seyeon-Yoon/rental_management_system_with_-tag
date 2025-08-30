import React from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  Button,
  Alert,
  Paper,
} from '@mui/material';
import {
  Dashboard,
  Inventory,
  Schedule,
  People,
  Warning,
  CheckCircle,
  TrendingUp,
  Assignment,
  Category as CategoryIcon,
  AccessTime,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { itemService } from '../../services/itemService';
import { categoryService } from '../../services/categoryService';
import { reservationService } from '../../services/reservationService';
import { rentalService } from '../../services/rentalService';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

interface StatCard {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'error';
  description?: string;
}

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();

  // 통계 데이터 조회
  const { data: itemStats, isLoading: itemLoading } = useQuery({
    queryKey: ['item-statistics'],
    queryFn: itemService.getItemStatistics,
  });

  const { data: categoryStats, isLoading: categoryLoading } = useQuery({
    queryKey: ['category-statistics'],
    queryFn: categoryService.getCategoryStatistics,
  });

  const { data: reservationStats, isLoading: reservationLoading } = useQuery({
    queryKey: ['reservation-statistics'],
    queryFn: reservationService.getReservationStatistics,
  });

  const { data: rentalStats, isLoading: rentalLoading } = useQuery({
    queryKey: ['rental-statistics'],
    queryFn: rentalService.getRentalStatistics,
  });

  // 최근 예약 조회
  const { data: recentReservations } = useQuery({
    queryKey: ['recent-reservations'],
    queryFn: () => reservationService.getReservations({ limit: 5 }),
  });

  // 연체된 대여 조회
  const { data: overdueRentals } = useQuery({
    queryKey: ['overdue-rentals'],
    queryFn: () => rentalService.getOverdueRentals({ limit: 5 }),
  });

  const isLoading = itemLoading || categoryLoading || reservationLoading || rentalLoading;

  if (isLoading) {
    return <Loading message="대시보드를 불러오는 중..." fullHeight />;
  }

  // 통계 카드 데이터
  const statCards: StatCard[] = [
    {
      title: '전체 품목',
      value: itemStats?.total_items || 0,
      icon: <Inventory />,
      color: 'primary',
      description: '등록된 전체 품목 수',
    },
    {
      title: '대여 가능',
      value: itemStats?.available_items || 0,
      icon: <CheckCircle />,
      color: 'success',
      description: '현재 대여 가능한 품목',
    },
    {
      title: '대여 중',
      value: itemStats?.rented_items || 0,
      icon: <Schedule />,
      color: 'warning',
      description: '현재 대여 중인 품목',
    },
    {
      title: '연체',
      value: rentalStats?.overdue_count || 0,
      icon: <Warning />,
      color: 'error',
      description: '반납 기한이 지난 품목',
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          관리자 대시보드
        </Typography>
        <Typography variant="body1" color="text.secondary">
          렌탈 시스템의 전체 현황을 한눈에 확인하세요.
        </Typography>
      </Box>

      {/* 통계 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Avatar
                    sx={{
                      bgcolor: `${stat.color}.main`,
                      width: 48,
                      height: 48,
                      mr: 2,
                    }}
                  >
                    {stat.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {stat.value.toLocaleString()}
                    </Typography>
                    <Typography variant="subtitle1" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
                {stat.description && (
                  <Typography variant="body2" color="text.secondary">
                    {stat.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* 최근 예약 현황 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Assignment sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="bold">
                  최근 예약 현황
                </Typography>
              </Box>

              {!recentReservations?.items || recentReservations.items.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                  최근 예약이 없습니다.
                </Typography>
              ) : (
                <List>
                  {recentReservations.items.map((reservation: any, index: number) => (
                    <React.Fragment key={reservation.id}>
                      <ListItem alignItems="flex-start" disablePadding>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            <Schedule />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={reservation.item?.name}
                          secondary={
                            <>
                              <Typography component="span" variant="body2">
                                {reservation.user?.name} ({reservation.user?.student_id})
                              </Typography>
                              <br />
                              <Typography component="span" variant="caption" color="text.secondary">
                                {dayjs(reservation.reserved_at).format('MM-DD HH:mm')} •{' '}
                                <Chip
                                  size="small"
                                  label={reservation.status === 'PENDING' ? '대기 중' : '확인됨'}
                                  color={reservation.status === 'PENDING' ? 'warning' : 'success'}
                                />
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                      {index < recentReservations.items.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => navigate('/admin/reservations')}
                >
                  전체 예약 관리
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 연체 현황 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Warning sx={{ mr: 1, color: 'error.main' }} />
                <Typography variant="h6" fontWeight="bold">
                  연체 현황
                </Typography>
              </Box>

              {!overdueRentals?.items || overdueRentals.items.length === 0 ? (
                <Alert severity="success">
                  현재 연체된 품목이 없습니다.
                </Alert>
              ) : (
                <>
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {overdueRentals.items.length}건의 연체된 품목이 있습니다.
                  </Alert>
                  <List>
                    {overdueRentals.items.map((rental: any, index: number) => {
                      const overdueDays = dayjs().diff(dayjs(rental.due_date), 'day');
                      
                      return (
                        <React.Fragment key={rental.id}>
                          <ListItem alignItems="flex-start" disablePadding>
                            <ListItemAvatar>
                              <Avatar sx={{ bgcolor: 'error.main' }}>
                                <Warning />
                              </Avatar>
                            </ListItemAvatar>
                            <ListItemText
                              primary={rental.item?.name}
                              secondary={
                                <>
                                  <Typography component="span" variant="body2">
                                    {rental.user?.name} ({rental.user?.student_id})
                                  </Typography>
                                  <br />
                                  <Typography component="span" variant="caption" color="error">
                                    {overdueDays}일 연체 • 반납 예정: {dayjs(rental.due_date).format('MM-DD')}
                                  </Typography>
                                </>
                              }
                            />
                          </ListItem>
                          {index < overdueRentals.items.length - 1 && <Divider />}
                        </React.Fragment>
                      );
                    })}
                  </List>
                </>
              )}

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  color="error"
                  onClick={() => navigate('/admin/rentals')}
                >
                  전체 대여 관리
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 카테고리별 현황 */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CategoryIcon sx={{ mr: 1 }} />
                <Typography variant="h6" fontWeight="bold">
                  카테고리별 현황
                </Typography>
              </Box>

              {categoryStats?.by_category ? (
                <Grid container spacing={2}>
                  {categoryStats.by_category.map((category: any) => (
                    <Grid item xs={12} sm={6} md={4} key={category.id}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {category.name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip size="small" label={`전체 ${category.total_items}`} />
                          <Chip size="small" label={`가능 ${category.available_items}`} color="success" />
                          <Chip size="small" label={`대여중 ${category.rented_items}`} color="warning" />
                        </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  카테고리 통계를 불러오는 중...
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 빠른 작업 버튼 */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          빠른 작업
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button
              variant="contained"
              startIcon={<Inventory />}
              onClick={() => navigate('/admin/items')}
            >
              품목 관리
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              startIcon={<Schedule />}
              onClick={() => navigate('/admin/reservations')}
            >
              예약 관리
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              startIcon={<Assignment />}
              onClick={() => navigate('/admin/rentals')}
            >
              대여 관리
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AdminDashboard;