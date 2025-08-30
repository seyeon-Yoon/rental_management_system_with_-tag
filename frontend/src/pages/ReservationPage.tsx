import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Schedule,
  Cancel,
  CheckCircle,
  AccessTime,
  Category as CategoryIcon,
  CalendarToday,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';
import { reservationService } from '../services/reservationService';
import { Reservation } from '../types';
import Loading from '../components/common/Loading';
import ErrorMessage from '../components/common/ErrorMessage';

const ReservationPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);

  // 내 활성 예약 조회
  const {
    data: reservations,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['my-reservations'],
    queryFn: reservationService.getMyActiveReservations,
    refetchInterval: 30000, // 30초마다 자동 새로고침
  });

  // 예약 취소 Mutation
  const cancelReservationMutation = useMutation({
    mutationFn: (reservationId: number) =>
      reservationService.cancelReservation(reservationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-reservations'] });
      queryClient.invalidateQueries({ queryKey: ['items'] });
      setCancelDialogOpen(false);
      setSelectedReservation(null);
    },
  });

  const getStatusColor = (status: string) => {
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

  const getStatusText = (status: string) => {
    switch (status) {
      case 'PENDING':
        return '예약 대기';
      case 'CONFIRMED':
        return '수령 완료';
      case 'EXPIRED':
        return '예약 만료';
      case 'CANCELLED':
        return '예약 취소';
      default:
        return status;
    }
  };

  const getRemainingTime = (expiresAt: string) => {
    const now = dayjs();
    const expiry = dayjs(expiresAt);
    const diff = expiry.diff(now);

    if (diff <= 0) {
      return { text: '만료됨', color: 'error' };
    }

    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    if (hours > 0) {
      return {
        text: `${hours}시간 ${remainingMinutes}분 남음`,
        color: hours >= 1 ? 'success' : 'warning',
      };
    } else {
      return {
        text: `${remainingMinutes}분 남음`,
        color: remainingMinutes >= 30 ? 'warning' : 'error',
      };
    }
  };

  const handleCancelClick = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setCancelDialogOpen(true);
  };

  const handleCancelConfirm = () => {
    if (selectedReservation) {
      cancelReservationMutation.mutate(selectedReservation.id);
    }
  };

  if (isLoading) {
    return <Loading message="예약 현황을 불러오는 중..." fullHeight />;
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorMessage
          title="예약 현황을 불러오는데 실패했습니다"
          message={error.message}
          onRetry={() => refetch()}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 페이지 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          내 예약 현황
        </Typography>
        <Typography variant="body1" color="text.secondary">
          현재 예약한 품목들을 확인하고 관리하세요.
        </Typography>
      </Box>

      {/* 안내 메시지 */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>안내사항:</strong> 예약 후 1시간 내에 학생회실에 방문하지 않으면 자동으로 취소됩니다.
        실시간 남은 시간을 확인하세요.
      </Alert>

      {/* 예약 목록 */}
      {!reservations || reservations.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Schedule sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            현재 활성화된 예약이 없습니다
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            품목 목록에서 원하는 품목을 예약해보세요
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {reservations.map((reservation: Reservation) => {
            const remainingTime = getRemainingTime(reservation.expires_at);
            const isExpired = reservation.status === 'EXPIRED';
            const isCancelled = reservation.status === 'CANCELLED';
            const isConfirmed = reservation.status === 'CONFIRMED';

            return (
              <Grid item xs={12} md={6} key={reservation.id}>
                <Card
                  sx={{
                    height: '100%',
                    opacity: isExpired || isCancelled ? 0.7 : 1,
                    border: isConfirmed ? 2 : 1,
                    borderColor: isConfirmed ? 'success.main' : 'divider',
                  }}
                >
                  <CardContent>
                    {/* 품목 정보 */}
                    <Typography variant="h6" component="h3" gutterBottom>
                      {reservation.item?.name}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <CategoryIcon sx={{ fontSize: 16, mr: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        {reservation.item?.category?.name}
                      </Typography>
                    </Box>

                    {reservation.item?.description && (
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {reservation.item.description}
                      </Typography>
                    )}

                    <Divider sx={{ my: 2 }} />

                    {/* 예약 상세 정보 */}
                    <List dense>
                      <ListItem disablePadding>
                        <ListItemText
                          primary="예약 시간"
                          secondary={dayjs(reservation.reserved_at).format('YYYY-MM-DD HH:mm')}
                          primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                        />
                      </ListItem>
                      
                      <ListItem disablePadding>
                        <ListItemText
                          primary="만료 시간"
                          secondary={dayjs(reservation.expires_at).format('YYYY-MM-DD HH:mm')}
                          primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                        />
                      </ListItem>

                      <ListItem disablePadding>
                        <ListItemText
                          primary="일련번호"
                          secondary={reservation.item?.serial_number}
                          primaryTypographyProps={{ variant: 'caption', fontWeight: 'bold' }}
                          secondaryTypographyProps={{ fontFamily: 'monospace' }}
                        />
                      </ListItem>
                    </List>

                    {/* 상태 및 남은 시간 */}
                    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                      <Chip
                        label={getStatusText(reservation.status)}
                        color={getStatusColor(reservation.status) as any}
                        size="small"
                        icon={
                          reservation.status === 'CONFIRMED' ? (
                            <CheckCircle />
                          ) : reservation.status === 'EXPIRED' ? (
                            <Cancel />
                          ) : (
                            <Schedule />
                          )
                        }
                      />
                      
                      {reservation.status === 'PENDING' && (
                        <Chip
                          label={remainingTime.text}
                          color={remainingTime.color as any}
                          size="small"
                          icon={<AccessTime />}
                        />
                      )}
                    </Box>
                  </CardContent>

                  <CardActions sx={{ px: 2, pb: 2 }}>
                    {reservation.status === 'PENDING' && !isExpired && (
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        startIcon={<Cancel />}
                        onClick={() => handleCancelClick(reservation)}
                        disabled={cancelReservationMutation.isPending}
                        fullWidth
                      >
                        예약 취소
                      </Button>
                    )}

                    {isConfirmed && (
                      <Alert severity="success" sx={{ width: '100%' }}>
                        수령 완료! 대여 기간은 7일입니다.
                      </Alert>
                    )}

                    {isExpired && (
                      <Alert severity="error" sx={{ width: '100%' }}>
                        예약이 만료되었습니다.
                      </Alert>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* 예약 취소 확인 다이얼로그 */}
      <Dialog
        open={cancelDialogOpen}
        onClose={() => setCancelDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>예약 취소</DialogTitle>
        <DialogContent>
          <Typography>
            <strong>{selectedReservation?.item?.name}</strong> 예약을 취소하시겠습니까?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            취소 후에는 다시 예약해야 합니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialogOpen(false)}>
            닫기
          </Button>
          <Button
            onClick={handleCancelConfirm}
            color="error"
            variant="contained"
            disabled={cancelReservationMutation.isPending}
          >
            {cancelReservationMutation.isPending ? '취소 중...' : '예약 취소'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ReservationPage;