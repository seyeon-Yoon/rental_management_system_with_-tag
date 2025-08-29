import axios, { AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError } from '@/types';

// Base URL 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - JWT 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response;
  },
  (error: AxiosError<ApiError>) => {
    // 401 에러 시 로그아웃 처리
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // 에러 메시지 표준화
    const errorMessage = error.response?.data?.detail || error.message || '알 수 없는 오류가 발생했습니다.';
    return Promise.reject(new Error(errorMessage));
  }
);

// API 헬퍼 함수들
export const api = {
  // GET 요청
  get: async <T>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get<ApiResponse<T>>(url, { params });
    return response.data.data;
  },

  // POST 요청
  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, data);
    return response.data.data;
  },

  // PUT 요청
  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put<ApiResponse<T>>(url, data);
    return response.data.data;
  },

  // DELETE 요청
  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete<ApiResponse<T>>(url);
    return response.data.data;
  },

  // PATCH 요청
  patch: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch<ApiResponse<T>>(url, data);
    return response.data.data;
  },
};