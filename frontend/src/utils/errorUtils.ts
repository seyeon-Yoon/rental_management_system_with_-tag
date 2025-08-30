import { AxiosError } from 'axios';
import { ApiError } from '@/types';

/**
 * API 에러에서 사용자 친화적인 메시지를 추출합니다.
 */
export const getErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as ApiError;
    return apiError?.detail || error.message || '서버 오류가 발생했습니다.';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return '알 수 없는 오류가 발생했습니다.';
};

/**
 * 에러가 특정 상태 코드인지 확인합니다.
 */
export const isErrorWithStatus = (error: unknown, status: number): boolean => {
  if (error instanceof AxiosError) {
    return error.response?.status === status;
  }
  return false;
};

/**
 * 401 Unauthorized 에러인지 확인합니다.
 */
export const isUnauthorizedError = (error: unknown): boolean => {
  return isErrorWithStatus(error, 401);
};

/**
 * 403 Forbidden 에러인지 확인합니다.
 */
export const isForbiddenError = (error: unknown): boolean => {
  return isErrorWithStatus(error, 403);
};

/**
 * 404 Not Found 에러인지 확인합니다.
 */
export const isNotFoundError = (error: unknown): boolean => {
  return isErrorWithStatus(error, 404);
};

/**
 * 네트워크 에러인지 확인합니다.
 */
export const isNetworkError = (error: unknown): boolean => {
  if (error instanceof AxiosError) {
    return error.code === 'ERR_NETWORK' || !error.response;
  }
  return false;
};