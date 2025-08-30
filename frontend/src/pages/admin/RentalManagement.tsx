import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  InputAdornment,
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
  Search,
  CheckCircle,
  Schedule,
  Warning,
  Cancel,
  Assignment,
  AccessTime,
  Person,
  Category as CategoryIcon,
  CalendarToday,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { reservationService } from '../../services/reservationService';
import { rentalService } from '../../services/rentalService';
import { Reservation, Rental } from '../../types';
import Loading from '../../components/common/Loading';
import ErrorMessage from '../../components/common/ErrorMessage';

const RentalManagement: React.FC = () => {
  const queryClient = useQueryClient();
  
  const [currentTab, setCurrentTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(1);
  
  // 다이얼로그 상태
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [returnDialogOpen, setReturnDialogOpen] = useState(false);
  const [extendDialogOpen, setExtendDialogOpen] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);
  const [selectedRental, setSelectedRental] = useState<Rental | null>(null);
  const [extendDays, setExtendDays] = useState(7);

  const itemsPerPage = 10;

  // 예약 목록 조회
  const {
    data: reservationsResponse,
    isLoading: reservationsLoading,
    error: reservationsError,
  } = useQuery({
    queryKey: ['admin-reservations', searchTerm, statusFilter, page],
    queryFn: () =>
      reservationService.getReservations({
        page,
        limit: itemsPerPage,
        status: statusFilter || undefined,
        // search는 백엔드에서 구현되지 않았으므로 주석 처리
        // search: searchTerm || undefined,
      }),
    enabled: currentTab === 0,
  });

  // 대여 목록 조회
  const {
    data: rentalsResponse,
    isLoading: rentalsLoading,
    error: rentalsError,
  } = useQuery({
    queryKey: ['admin-rentals', searchTerm, statusFilter, page],
    queryFn: () =>
      rentalService.getRentals({
        page,
        limit: itemsPerPage,
        status: statusFilter || undefined,
        // search는 백엔드에서 구현되지 않았으므로 주석 처리
      }),
    enabled: currentTab === 1,
  });

  // 예약 확인 Mutation
  const confirmReservationMutation = useMutation({
    mutationFn: (id: number) => reservationService.confirmReservation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-reservations'] });
      queryClient.invalidateQueries({ queryKey: ['admin-rentals'] });
      setConfirmDialogOpen(false);
      setSelectedReservation(null);
    },
  });

  // 대여 반납 Mutation
  const returnRentalMutation = useMutation({
    mutationFn: (id: number) => rentalService.returnRental(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-rentals'] });
      queryClient.invalidateQueries({ queryKey: ['item-statistics'] });
      setReturnDialogOpen(false);
      setSelectedRental(null);
    },
  });

  // 대여 연장 Mutation
  const extendRentalMutation = useMutation({
    mutationFn: ({ id, days }: { id: number; days: number }) =>
      rentalService.extendRental(id, { days }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-rentals'] });
      setExtendDialogOpen(false);
      setSelectedRental(null);
    },
  });

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
    setPage(1);
    setSearchTerm('');
    setStatusFilter('');
  };

  const handleConfirmReservation = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setConfirmDialogOpen(true);
  };

  const handleReturnRental = (rental: Rental) => {
    setSelectedRental(rental);
    setReturnDialogOpen(true);
  };

  const handleExtendRental = (rental: Rental) => {
    setSelectedRental(rental);
    setExtendDays(7);
    setExtendDialogOpen(true);
  };

  const getReservationStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return 'warning';
      case 'CONFIRMED':
        return 'success';
      case 'EXPIRED':
        return 'error';
      case 'CANCELLED':
        return 'default';
      default:
        return 'default';
    }
  };

  const getRentalStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'RETURNED':
        return 'info';
      case 'OVERDUE':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRemainingTime = (expiresAt: string) => {
    const now = dayjs();
    const expiry = dayjs(expiresAt);
    const diff = expiry.diff(now, 'minute');

    if (diff <= 0) return '만료됨';
    
    const hours = Math.floor(diff / 60);
    const minutes = diff % 60;
    
    if (hours > 0) {
      return `${hours}시간 ${minutes}분`;
    } else {
      return `${minutes}분`;
    }
  };

  const getRemainingDays = (dueDate: string) => {
    const now = dayjs();
    const due = dayjs(dueDate);
    const diff = due.diff(now, 'day');

    if (diff < 0) {
      return `${Math.abs(diff)}일 연체`;
    } else if (diff === 0) {
      return '오늘 반납';
    } else {
      return `${diff}일 남음`;
    }
  };

  const isLoading = currentTab === 0 ? reservationsLoading : rentalsLoading;
  const error = currentTab === 0 ? reservationsError : rentalsError;

  if (isLoading && page === 1) {
    return <Loading message="데이터를 불러오는 중..." fullHeight />;
  }

  const renderReservations = () => {
    const reservations = reservationsResponse?.items || [];
    const totalPages = Math.ceil((reservationsResponse?.total || 0) / itemsPerPage);

    if (reservations.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Assignment sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            조건에 맞는 예약이 없습니다
          </Typography>
        </Box>
      );
    }

    return (
      <>
        <Grid container spacing={2}>
          {reservations.map((reservation: Reservation) => (
            <Grid item xs={12} key={reservation.id}>
              <Card variant="outlined">
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={3}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {reservation.item?.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {reservation.item?.category?.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {reservation.item?.serial_number}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Person sx={{ fontSize: 16, mr: 1 }} />
                        <Typography variant="body2">
                          {reservation.user?.name}
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {reservation.user?.student_id} • {reservation.user?.department}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>예약:</strong> {dayjs(reservation.reserved_at).format('MM-DD HH:mm')}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>만료:</strong> {dayjs(reservation.expires_at).format('MM-DD HH:mm')}
                      </Typography>
                      {reservation.status === 'PENDING' && (
                        <Typography variant="caption" color="warning.main">
                          남은 시간: {getRemainingTime(reservation.expires_at)}
                        </Typography>
                      )}
                    </Grid>

                    <Grid item xs={12} md={3} sx={{ textAlign: 'right' }}>
                      <Box sx={{ mb: 1 }}>
                        <Chip
                          size="small"
                          label={
                            reservation.status === 'PENDING' ? '대기 중' :
                            reservation.status === 'CONFIRMED' ? '확인됨' :
                            reservation.status === 'EXPIRED' ? '만료됨' :
                            '취소됨'
                          }
                          color={getReservationStatusColor(reservation.status) as any}
                        />
                      </Box>
                      {reservation.status === 'PENDING' && (
                        <Button
                          size="small"
                          variant="contained"
                          color="primary"
                          onClick={() => handleConfirmReservation(reservation)}
                        >
                          수령 확인
                        </Button>
                      )}
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

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

  const renderRentals = () => {
    const rentals = rentalsResponse?.items || [];
    const totalPages = Math.ceil((rentalsResponse?.total || 0) / itemsPerPage);

    if (rentals.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Schedule sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            조건에 맞는 대여가 없습니다
          </Typography>
        </Box>
      );
    }

    return (
      <>
        <Grid container spacing={2}>
          {rentals.map((rental: Rental) => (
            <Grid item xs={12} key={rental.id}>
              <Card 
                variant="outlined"
                sx={{
                  borderColor: rental.status === 'OVERDUE' ? 'error.main' : 'divider',
                  borderWidth: rental.status === 'OVERDUE' ? 2 : 1,
                }}
              >
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={3}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {rental.item?.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {rental.item?.category?.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {rental.item?.serial_number}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} md={2}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Person sx={{ fontSize: 16, mr: 1 }} />
                        <Typography variant="body2">
                          {rental.user?.name}
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {rental.user?.student_id}
                      </Typography>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>대여:</strong> {dayjs(rental.rental_date).format('MM-DD')}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>반납 예정:</strong> {dayjs(rental.due_date).format('MM-DD')}
                      </Typography>
                      {rental.return_date && (
                        <Typography variant="body2">
                          <strong>실제 반납:</strong> {dayjs(rental.return_date).format('MM-DD')}
                        </Typography>
                      )}
                      {rental.status === 'ACTIVE' && (
                        <Typography 
                          variant="caption" 
                          color={dayjs(rental.due_date).isBefore(dayjs()) ? 'error.main' : 'text.secondary'}
                        >
                          {dayjs(rental.due_date).isBefore(dayjs()) 
                            ? `${dayjs().diff(dayjs(rental.due_date), 'day')}일 연체` 
                            : `${dayjs(rental.due_date).diff(dayjs(), 'day')}일 남음`}
                        </Typography>
                      )}
                    </Grid>

                    <Grid item xs={12} md={2}>
                      <Chip
                        size="small"
                        label={
                          rental.status === 'ACTIVE' ? '대여 중' :
                          rental.status === 'RETURNED' ? '반납됨' :
                          rental.status === 'OVERDUE' ? '연체' :
                          rental.status
                        }
                        color={getRentalStatusColor(rental.status) as any}
                        icon={
                          rental.status === 'OVERDUE' ? <Warning /> :
                          rental.status === 'RETURNED' ? <CheckCircle /> :
                          <Schedule />
                        }
                      />
                    </Grid>

                    <Grid item xs={12} md={2} sx={{ textAlign: 'right' }}>
                      {rental.status === 'ACTIVE' && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                          <Button
                            size="small"
                            variant="contained"
                            color="primary"
                            onClick={() => handleReturnRental(rental)}
                          >
                            반납 처리
                          </Button>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleExtendRental(rental)}
                          >
                            연장
                          </Button>
                        </Box>
                      )}
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

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
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          대여 관리
        </Typography>
        <Typography variant="body1" color="text.secondary">
          예약 확인과 대여 반납을 관리하세요.
        </Typography>
      </Box>

      {/* 탭 메뉴 */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab
            label="예약 관리"
            icon={<Assignment />}
            iconPosition="start"
          />
          <Tab
            label="대여 관리"
            icon={<Schedule />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* 검색 및 필터 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="사용자명 또는 품목명으로 검색..."
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
                <InputLabel>상태</InputLabel>
                <Select
                  value={statusFilter}
                  label="상태"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">전체 상태</MenuItem>
                  {currentTab === 0 ? (
                    <>
                      <MenuItem value="PENDING">대기 중</MenuItem>
                      <MenuItem value="CONFIRMED">확인됨</MenuItem>
                      <MenuItem value="EXPIRED">만료됨</MenuItem>
                      <MenuItem value="CANCELLED">취소됨</MenuItem>
                    </>
                  ) : (
                    <>
                      <MenuItem value="ACTIVE">대여 중</MenuItem>
                      <MenuItem value="RETURNED">반납됨</MenuItem>
                      <MenuItem value="OVERDUE">연체</MenuItem>
                    </>
                  )}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 에러 처리 */}
      {error && (
        <ErrorMessage
          title={`${currentTab === 0 ? '예약' : '대여'} 데이터를 불러오는데 실패했습니다`}
          message={error.message}
        />
      )}

      {/* 탭 콘텐츠 */}
      {currentTab === 0 ? renderReservations() : renderRentals()}

      {/* 예약 확인 다이얼로그 */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>예약 수령 확인</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            다음 예약의 수령을 확인하시겠습니까?
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary={`품목: ${selectedReservation?.item?.name}`}
                secondary={`사용자: ${selectedReservation?.user?.name} (${selectedReservation?.user?.student_id})`}
              />
            </ListItem>
          </List>
          <Alert severity="info">
            확인 시 자동으로 대여가 시작됩니다. (대여 기간: 7일)
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>
            취소
          </Button>
          <Button
            onClick={() => selectedReservation && confirmReservationMutation.mutate(selectedReservation.id)}
            variant="contained"
            disabled={confirmReservationMutation.isPending}
          >
            {confirmReservationMutation.isPending ? '처리 중...' : '수령 확인'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 반납 처리 다이얼로그 */}
      <Dialog
        open={returnDialogOpen}
        onClose={() => setReturnDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>반납 처리</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            다음 대여의 반납을 처리하시겠습니까?
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary={`품목: ${selectedRental?.item?.name}`}
                secondary={`사용자: ${selectedRental?.user?.name} (${selectedRental?.user?.student_id})`}
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReturnDialogOpen(false)}>
            취소
          </Button>
          <Button
            onClick={() => selectedRental && returnRentalMutation.mutate(selectedRental.id)}
            variant="contained"
            disabled={returnRentalMutation.isPending}
          >
            {returnRentalMutation.isPending ? '처리 중...' : '반납 처리'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 연장 처리 다이얼로그 */}
      <Dialog
        open={extendDialogOpen}
        onClose={() => setExtendDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>대여 연장</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            대여 기간을 연장하시겠습니까?
          </Typography>
          <List sx={{ mb: 2 }}>
            <ListItem>
              <ListItemText
                primary={`품목: ${selectedRental?.item?.name}`}
                secondary={`사용자: ${selectedRental?.user?.name} (${selectedRental?.user?.student_id})`}
              />
            </ListItem>
          </List>
          
          <FormControl fullWidth>
            <InputLabel>연장 일수</InputLabel>
            <Select
              value={extendDays}
              label="연장 일수"
              onChange={(e) => setExtendDays(e.target.value as number)}
            >
              <MenuItem value={1}>1일</MenuItem>
              <MenuItem value={3}>3일</MenuItem>
              <MenuItem value={5}>5일</MenuItem>
              <MenuItem value={7}>7일</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExtendDialogOpen(false)}>
            취소
          </Button>
          <Button
            onClick={() => selectedRental && extendRentalMutation.mutate({ id: selectedRental.id, days: extendDays })}
            variant="contained"
            disabled={extendRentalMutation.isPending}
          >
            {extendRentalMutation.isPending ? '처리 중...' : '연장'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default RentalManagement;