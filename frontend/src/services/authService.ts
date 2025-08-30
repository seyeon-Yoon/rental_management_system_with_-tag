import { api, apiClient } from './api';
import { User, LoginRequest, LoginResponse } from '../types';

export const authService = {
  // 로그인 - 직접 응답 형식 사용 (ApiResponse 래퍼 없음)
  login: async (studentId: string, password: string): Promise<LoginResponse> => {
    const loginData: LoginRequest = {
      student_id: studentId,
      password,
    };
    const response = await apiClient.post<LoginResponse>('/auth/login', loginData);
    return response.data;
  },

  // 로그아웃
  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      // 로그아웃 요청 실패해도 로컬 스토리지는 정리
      console.error('서버 로그아웃 실패:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },

  // 현재 사용자 정보 조회
  getCurrentUser: async (): Promise<User> => {
    return api.get<User>('/auth/me');
  },

  // 토큰 갱신 - 직접 응답 형식 사용 (ApiResponse 래퍼 없음)
  refreshToken: async (): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/refresh');
    return response.data;
  },
};