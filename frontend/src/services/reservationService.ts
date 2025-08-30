import { api } from './api';
import { Reservation, PaginatedResponse, PaginationParams } from '../types';

interface ReservationSearchParams extends PaginationParams {
  status?: string;
  user_id?: number;
  item_id?: number;
}

interface CreateReservationData {
  item_id: number;
}

export const reservationService = {
  // 예약 목록 조회
  getReservations: async (params?: ReservationSearchParams): Promise<PaginatedResponse<Reservation>> => {
    return api.get<PaginatedResponse<Reservation>>('/reservations', params);
  },

  // 내 활성 예약 조회 (학생용)
  getMyActiveReservations: async (): Promise<Reservation[]> => {
    return api.get<Reservation[]>('/reservations/my');
  },

  // 예약 상세 조회
  getReservation: async (id: number): Promise<Reservation> => {
    return api.get<Reservation>(`/reservations/${id}`);
  },

  // 새 예약 생성
  createReservation: async (data: CreateReservationData): Promise<Reservation> => {
    return api.post<Reservation>('/reservations', data);
  },

  // 예약 수령 확인 (관리자 전용)
  confirmReservation: async (id: number): Promise<Reservation> => {
    return api.post<Reservation>(`/reservations/${id}/confirm`);
  },

  // 예약 취소
  cancelReservation: async (id: number): Promise<Reservation> => {
    return api.post<Reservation>(`/reservations/${id}/cancel`);
  },

  // 만료된 예약 일괄 처리 (관리자 전용)
  expireReservations: async (): Promise<{ expired_count: number }> => {
    return api.post<{ expired_count: number }>('/reservations/expire');
  },

  // 예약 통계 조회 (관리자 전용)
  getReservationStatistics: async (): Promise<any> => {
    return api.get<any>('/reservations/statistics');
  },

  // 사용자별 예약 조회 (관리자 전용)
  getUserReservations: async (userId: number, params?: PaginationParams): Promise<PaginatedResponse<Reservation>> => {
    return api.get<PaginatedResponse<Reservation>>('/reservations', {
      ...params,
      user_id: userId
    });
  },

  // 품목별 예약 조회 (관리자 전용)
  getItemReservations: async (itemId: number, params?: PaginationParams): Promise<PaginatedResponse<Reservation>> => {
    return api.get<PaginatedResponse<Reservation>>('/reservations', {
      ...params,
      item_id: itemId
    });
  },
};