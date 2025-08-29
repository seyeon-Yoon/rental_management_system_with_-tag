// 사용자 관련 타입
export interface User {
  id: number;
  student_id: string;
  name: string;
  department: string;
  email?: string;
  role: 'STUDENT' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

// 카테고리 관련 타입
export interface Category {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

// 품목 관련 타입
export interface Item {
  id: number;
  category_id: number;
  category?: Category;
  name: string;
  description?: string;
  serial_number: string;
  status: 'AVAILABLE' | 'RESERVED' | 'RENTED' | 'MAINTENANCE';
  metadata?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 예약 관련 타입
export interface Reservation {
  id: number;
  user_id: number;
  user?: User;
  item_id: number;
  item?: Item;
  reserved_at: string;
  expires_at: string;
  status: 'PENDING' | 'CONFIRMED' | 'EXPIRED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
}

// 대여 관련 타입
export interface Rental {
  id: number;
  user_id: number;
  user?: User;
  item_id: number;
  item?: Item;
  rental_date: string;
  due_date: string;
  return_date?: string;
  status: 'ACTIVE' | 'RETURNED' | 'OVERDUE';
  created_at: string;
  updated_at: string;
}

// API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  timestamp: string;
}

// 페이지네이션 타입
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// 인증 관련 타입
export interface LoginRequest {
  student_id: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 필터 타입
export interface ItemFilter {
  category_id?: number;
  status?: string;
  available_only?: boolean;
  search?: string;
}

// 에러 타입
export interface ApiError {
  detail: string;
  code?: string;
}