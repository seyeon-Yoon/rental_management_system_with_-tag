import { api } from './api';
import { User, LoginRequest, LoginResponse } from '../types';

export const authService = {
  // 로그인
  login: async (studentId: string, password: string): Promise<LoginResponse> => {
    const loginData: LoginRequest = {
      student_id: studentId,
      password,
    };
    return api.post<LoginResponse>('/auth/login', loginData);
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

  // 토큰 갱신
  refreshToken: async (): Promise<LoginResponse> => {
    return api.post<LoginResponse>('/auth/refresh');
  },
};