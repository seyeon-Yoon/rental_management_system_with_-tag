import { api } from './api';
import { Category, PaginatedResponse, PaginationParams } from '../types';

export const categoryService = {
  // 카테고리 목록 조회
  getCategories: async (params?: PaginationParams): Promise<PaginatedResponse<Category>> => {
    return api.get<PaginatedResponse<Category>>('/categories', params);
  },

  // 카테고리 상세 조회
  getCategory: async (id: number): Promise<Category> => {
    return api.get<Category>(`/categories/${id}`);
  },

  // 카테고리 생성 (관리자 전용)
  createCategory: async (data: Partial<Category>): Promise<Category> => {
    return api.post<Category>('/categories', data);
  },

  // 카테고리 수정 (관리자 전용)
  updateCategory: async (id: number, data: Partial<Category>): Promise<Category> => {
    return api.put<Category>(`/categories/${id}`, data);
  },

  // 카테고리 삭제 (관리자 전용)
  deleteCategory: async (id: number): Promise<void> => {
    return api.delete<void>(`/categories/${id}`);
  },

  // 카테고리 통계 조회 (관리자 전용)
  getCategoryStatistics: async (): Promise<any> => {
    return api.get<any>('/categories/statistics');
  },
};