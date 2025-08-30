import dayjs, { Dayjs } from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/ko';

// 한국어 로케일과 상대시간 플러그인 설정
dayjs.extend(relativeTime);
dayjs.locale('ko');

/**
 * 날짜를 한국어 형식으로 포맷합니다.
 */
export const formatDate = (date: string | Date | Dayjs): string => {
  return dayjs(date).format('YYYY년 MM월 DD일 HH:mm');
};

/**
 * 날짜를 짧은 형식으로 포맷합니다.
 */
export const formatDateShort = (date: string | Date | Dayjs): string => {
  return dayjs(date).format('MM/DD HH:mm');
};

/**
 * 상대적인 시간을 반환합니다. (예: 3시간 전)
 */
export const formatRelativeTime = (date: string | Date | Dayjs): string => {
  return dayjs(date).fromNow();
};

/**
 * 두 날짜 간의 차이를 분 단위로 반환합니다.
 */
export const getDifferenceInMinutes = (
  date1: string | Date | Dayjs, 
  date2: string | Date | Dayjs = dayjs()
): number => {
  return dayjs(date2).diff(dayjs(date1), 'minute');
};

/**
 * 두 날짜 간의 차이를 일 단위로 반환합니다.
 */
export const getDifferenceInDays = (
  date1: string | Date | Dayjs, 
  date2: string | Date | Dayjs = dayjs()
): number => {
  return dayjs(date2).diff(dayjs(date1), 'day');
};

/**
 * 날짜가 현재보다 과거인지 확인합니다.
 */
export const isPast = (date: string | Date | Dayjs): boolean => {
  return dayjs(date).isBefore(dayjs());
};

/**
 * 날짜가 현재보다 미래인지 확인합니다.
 */
export const isFuture = (date: string | Date | Dayjs): boolean => {
  return dayjs(date).isAfter(dayjs());
};

/**
 * 날짜가 오늘인지 확인합니다.
 */
export const isToday = (date: string | Date | Dayjs): boolean => {
  return dayjs(date).isSame(dayjs(), 'day');
};

/**
 * 대여 기간 종료까지 남은 시간을 포맷합니다.
 */
export const formatRemainingTime = (endDate: string | Date | Dayjs): string => {
  const now = dayjs();
  const end = dayjs(endDate);
  
  if (end.isBefore(now)) {
    return '기간 만료';
  }
  
  const diffDays = end.diff(now, 'day');
  const diffHours = end.diff(now, 'hour') % 24;
  const diffMinutes = end.diff(now, 'minute') % 60;
  
  if (diffDays > 0) {
    return `${diffDays}일 ${diffHours}시간 남음`;
  } else if (diffHours > 0) {
    return `${diffHours}시간 ${diffMinutes}분 남음`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes}분 남음`;
  } else {
    return '곧 만료';
  }
};