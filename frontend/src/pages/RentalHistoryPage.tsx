import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider,
  Tabs,
  Tab,
  Alert,
  Pagination,
} from '@mui/material';
import {
  History,
  CheckCircle,
  Schedule,
  Warning,
  Category as CategoryIcon,
  CalendarToday,
  AccessTime,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { rentalService } from '../services/rentalService';
import { Rental } from '../types';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const RentalHistoryPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [page, setPage] = useState(1);
  
  const itemsPerPage = 10;

  // 내 활성 대여 조회
  const {
    data: activeRentals,
    isLoading: activeLoading,
    error: activeError,
  } = useQuery({
    queryKey: ['my-active-rentals'],
    queryFn: rentalService.getMyActiveRentals,
    refetchInterval: 60000, // 1분마다 자동 새로고침
  });

  // 전체 대여 이력 조회 (페이지네이션)
  const {
    data: rentalHistory,
    isLoading: historyLoading,
    error: historyError,
  } = useQuery({
    queryKey: ['my-rental-history', page],
    queryFn: () => rentalService.getRentalHistory({ page, limit: itemsPerPage }),
    enabled: currentTab === 1, // 이력 탭이 활성화된 경우만 조회
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'RETURNED':
        return 'info';
      case 'OVERDUE':
        return 'error';
      case 'LOST':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return '대여 중';
      case 'RETURNED':
        return '반납 완료';
      case 'OVERDUE':
        return '연체';
      case 'LOST':
        return '분실';
      default:
        return status;
    }
  };

  const getRemainingDays = (dueDate: string) => {
    const now = dayjs();
    const due = dayjs(dueDate);
    const diff = due.diff(now, 'day');

    if (diff < 0) {
      return {
        text: `${Math.abs(diff)}일 연체`,
        color: 'error',
      };
    } else if (diff === 0) {
      return {
        text: '오늘 반납',
        color: 'warning',
      };
    } else if (diff <= 2) {
      return {
        text: `${diff}일 남음`,
        color: 'warning',
      };
    } else {
      return {
        text: `${diff}일 남음`,
        color: 'success',
      };
    }
  };

  const getTotalRentalDays = (rentalDate: string, returnDate?: string) => {
    const start = dayjs(rentalDate);
    const end = returnDate ? dayjs(returnDate) : dayjs();
    return end.diff(start, 'day');
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
    setPage(1); // 탭 변경 시 페이지 리셋
  };

  const isLoading = currentTab === 0 ? activeLoading : historyLoading;
  const error = currentTab === 0 ? activeError : historyError;

  if (isLoading) {
    return <Loading message="대여 이력을 불러오는 중..." fullHeight />;
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorMessage
          title="대여 이력을 불러오는데 실패했습니다"
          message={error.message}
        />
      </Container>
    );
  }

  const renderActiveRentals = () => {
    if (!activeRentals || activeRentals.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Schedule sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            현재 대여 중인 품목이 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            품목을 예약하고 수령하면 여기에 표시됩니다
          </Typography>
        </Box>
      );
    }

    return (
      <Grid container spacing={3}>
        {activeRentals.map((rental: Rental) => {
          const remainingDays = getRemainingDays(rental.due_date);
          const isOverdue = rental.status === 'OVERDUE';

          return (
            <Grid item xs={12} md={6} key={rental.id}>
              <Card
                sx={{
                  height: '100%',
                  border: isOverdue ? 2 : 1,
                  borderColor: isOverdue ? 'error.main' : 'divider',
                }}
              >
                <CardContent>
                  <Typography variant="h6" component="h3" gutterBottom>
                    {rental.item?.name}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CategoryIcon sx={{ fontSize: 16, mr: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      {rental.item?.category?.name}
                    </Typography>
                  </Box>

                  {rental.item?.description && (
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {rental.item.description}
                    </Typography>
                  )}

                  <Divider sx={{ my: 2 }} />

                  <List dense>
                    <ListItem disablePadding>
                      <ListItemText
                        primary="대여 일시"
                        secondary={dayjs(rental.rental_date).format('YYYY-MM-DD HH:mm')}
                        primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                      />
                    </ListItem>
                    
                    <ListItem disablePadding>
                      <ListItemText
                        primary="반납 예정일"
                        secondary={dayjs(rental.due_date).format('YYYY-MM-DD')}
                        primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                      />
                    </ListItem>

                    <ListItem disablePadding>
                      <ListItemText
                        primary="일련번호"
                        secondary={rental.item?.serial_number}
                        primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                        secondaryTypographyProps={{ fontFamily: 'monospace' }}
                      />
                    </ListItem>
                  </List>

                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Chip
                      label={getStatusText(rental.status)}
                      color={getStatusColor(rental.status) as any}
                      size="small"
                      icon={rental.status === 'OVERDUE' ? <Warning /> : <CheckCircle />}
                    />
                    
                    <Chip
                      label={remainingDays.text}
                      color={remainingDays.color as any}
                      size="small"
                      icon={<AccessTime />}
                    />
                  </Box>

                  {isOverdue && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      반납 기한이 지났습니다. 빠른 시일 내에 반납해주세요.
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    );
  };

  const renderRentalHistory = () => {
    const rentals = rentalHistory?.items || [];
    const totalPages = Math.ceil((rentalHistory?.total || 0) / itemsPerPage);

    if (rentals.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <History sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            대여 이력이 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            품목을 대여하면 이력이 여기에 표시됩니다
          </Typography>
        </Box>
      );
    }

    return (
      <>
        <Grid container spacing={2}>
          {rentals.map((rental: Rental) => {
            const totalDays = getTotalRentalDays(rental.rental_date, rental.return_date);

            return (
              <Grid item xs={12} key={rental.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Grid container spacing={2} alignItems="center">
                      {/* 품목 정보 */}
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {rental.item?.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {rental.item?.category?.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {rental.item?.serial_number}
                        </Typography>
                      </Grid>

                      {/* 대여 정보 */}
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2">
                          <strong>대여:</strong> {dayjs(rental.rental_date).format('YYYY-MM-DD')}
                        </Typography>
                        <Typography variant="body2">
                          <strong>반납 예정:</strong> {dayjs(rental.due_date).format('YYYY-MM-DD')}
                        </Typography>
                        {rental.return_date && (
                          <Typography variant="body2">
                            <strong>실제 반납:</strong> {dayjs(rental.return_date).format('YYYY-MM-DD')}
                          </Typography>
                        )}
                        <Typography variant="body2">
                          <strong>대여 기간:</strong> {totalDays}일
                        </Typography>
                      </Grid>

                      {/* 상태 */}
                      <Grid item xs={12} sm={4} sx={{ textAlign: { xs: 'left', sm: 'right' } }}>
                        <Chip
                          label={getStatusText(rental.status)}
                          color={getStatusColor(rental.status) as any}
                          icon={
                            rental.status === 'RETURNED' ? <CheckCircle /> :
                            rental.status === 'OVERDUE' ? <Warning /> :
                            <Schedule />
                          }
                        />
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, value) => setPage(value)}
              color="primary"
            />
          </Box>
        )}
      </>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          대여 이력
        </Typography>
        <Typography variant="body1" color="text.secondary">
          현재 대여 중인 품목과 과거 대여 이력을 확인하세요.
        </Typography>
      </Box>

      {/* 탭 메뉴 */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab
            label={`현재 대여 중 (${activeRentals?.length || 0})`}
            icon={<Schedule />}
            iconPosition="start"
          />
          <Tab
            label="전체 이력"
            icon={<History />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* 안내 메시지 */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>안내사항:</strong> 대여 기간은 7일이며, 필요 시 연장 신청이 가능합니다. 
        연체 시 추가 대여가 제한될 수 있습니다.
      </Alert>

      {/* 탭 콘텐츠 */}
      {currentTab === 0 ? renderActiveRentals() : renderRentalHistory()}
    </Container>
  );
};

export default RentalHistoryPage;