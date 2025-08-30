import { api } from './api';
import { Rental, PaginatedResponse, PaginationParams } from '../types';

interface RentalSearchParams extends PaginationParams {
  status?: string;
  user_id?: number;
  item_id?: number;
  overdue?: boolean;
}

interface ExtendRentalData {
  days: number; // 1-7일
}

export const rentalService = {
  // 대여 목록 조회
  getRentals: async (params?: RentalSearchParams): Promise<PaginatedResponse<Rental>> => {
    return api.get<PaginatedResponse<Rental>>('/rentals', params);
  },

  // 내 활성 대여 조회 (학생용)
  getMyActiveRentals: async (): Promise<Rental[]> => {
    return api.get<Rental[]>('/rentals/my');
  },

  // 대여 상세 조회
  getRental: async (id: number): Promise<Rental> => {
    return api.get<Rental>(`/rentals/${id}`);
  },

  // 대여 반납 처리 (관리자 전용)
  returnRental: async (id: number): Promise<Rental> => {
    return api.post<Rental>(`/rentals/${id}/return`);
  },

  // 대여 연장 처리 (관리자 전용)
  extendRental: async (id: number, data: ExtendRentalData): Promise<Rental> => {
    return api.post<Rental>(`/rentals/${id}/extend`, data);
  },

  // 연체된 대여 일괄 처리 (관리자 전용)
  processOverdueRentals: async (): Promise<{ overdue_count: number }> => {
    return api.post<{ overdue_count: number }>('/rentals/overdue');
  },

  // 대여 이력 통계 조회 (관리자 전용)
  getRentalHistory: async (params?: PaginationParams): Promise<PaginatedResponse<any>> => {
    return api.get<PaginatedResponse<any>>('/rentals/history', params);
  },

  // 대여 통계 조회 (관리자 전용)
  getRentalStatistics: async (): Promise<any> => {
    return api.get<any>('/rentals/statistics');
  },

  // 사용자별 대여 조회 (관리자 전용)
  getUserRentals: async (userId: number, params?: PaginationParams): Promise<PaginatedResponse<Rental>> => {
    return api.get<PaginatedResponse<Rental>>('/rentals', {
      ...params,
      user_id: userId
    });
  },

  // 품목별 대여 조회 (관리자 전용)
  getItemRentals: async (itemId: number, params?: PaginationParams): Promise<PaginatedResponse<Rental>> => {
    return api.get<PaginatedResponse<Rental>>('/rentals', {
      ...params,
      item_id: itemId
    });
  },

  // 연체 대여 목록 조회 (관리자 전용)
  getOverdueRentals: async (params?: PaginationParams): Promise<PaginatedResponse<Rental>> => {
    return api.get<PaginatedResponse<Rental>>('/rentals', {
      ...params,
      overdue: true
    });
  },
};