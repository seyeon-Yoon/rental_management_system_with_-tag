import { api } from './api';
import { Item, PaginatedResponse, PaginationParams, ItemFilter } from '../types';

interface ItemSearchParams extends PaginationParams {
  category_id?: number;
  status?: string;
  available_only?: boolean;
  search?: string;
}

export const itemService = {
  // 품목 목록 조회 (검색, 필터링 지원)
  getItems: async (params?: ItemSearchParams): Promise<PaginatedResponse<Item>> => {
    return api.get<PaginatedResponse<Item>>('/items', params);
  },

  // 대여 가능한 품목만 조회
  getAvailableItems: async (params?: PaginationParams): Promise<PaginatedResponse<Item>> => {
    return api.get<PaginatedResponse<Item>>('/items/available', params);
  },

  // 품목 상세 조회
  getItem: async (id: number): Promise<Item> => {
    return api.get<Item>(`/items/${id}`);
  },

  // 일련번호로 품목 조회
  getItemBySerial: async (serialNumber: string): Promise<Item> => {
    return api.get<Item>(`/items/serial/${encodeURIComponent(serialNumber)}`);
  },

  // 품목 생성 (관리자 전용)
  createItem: async (data: Partial<Item>): Promise<Item> => {
    return api.post<Item>('/items', data);
  },

  // 품목 수정 (관리자 전용)
  updateItem: async (id: number, data: Partial<Item>): Promise<Item> => {
    return api.put<Item>(`/items/${id}`, data);
  },

  // 품목 삭제 (관리자 전용)
  deleteItem: async (id: number): Promise<void> => {
    return api.delete<void>(`/items/${id}`);
  },

  // 품목 통계 조회 (관리자 전용)
  getItemStatistics: async (): Promise<any> => {
    return api.get<any>('/items/statistics');
  },

  // 카테고리별 품목 조회
  getItemsByCategory: async (categoryId: number, params?: PaginationParams): Promise<PaginatedResponse<Item>> => {
    return api.get<PaginatedResponse<Item>>('/items', { 
      ...params,
      category_id: categoryId 
    });
  },

  // 품목 검색
  searchItems: async (searchTerm: string, params?: PaginationParams): Promise<PaginatedResponse<Item>> => {
    return api.get<PaginatedResponse<Item>>('/items', {
      ...params,
      search: searchTerm
    });
  },
};