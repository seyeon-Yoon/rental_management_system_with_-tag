import { useState, useCallback } from 'react';

export interface UseErrorReturn {
  error: string | null;
  setError: (error: string | null) => void;
  clearError: () => void;
  handleError: (error: unknown) => void;
}

export const useError = (): UseErrorReturn => {
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((error: unknown) => {
    if (error instanceof Error) {
      setError(error.message);
    } else if (typeof error === 'string') {
      setError(error);
    } else {
      setError('알 수 없는 오류가 발생했습니다.');
    }
  }, []);

  return {
    error,
    setError,
    clearError,
    handleError,
  };
};

export default useError;