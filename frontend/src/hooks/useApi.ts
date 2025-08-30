import { useState, useCallback } from 'react';
import { useError } from './useError';
import { useLoading } from './useLoading';

export interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (apiCall: () => Promise<T>) => Promise<T | null>;
  reset: () => void;
  clearError: () => void;
}

export const useApi = <T = any>(): UseApiReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const { loading, withLoading } = useLoading();
  const { error, handleError, clearError } = useError();

  const execute = useCallback(async (apiCall: () => Promise<T>): Promise<T | null> => {
    try {
      clearError();
      const result = await withLoading(apiCall);
      setData(result);
      return result;
    } catch (err) {
      handleError(err);
      setData(null);
      return null;
    }
  }, [withLoading, handleError, clearError]);

  const reset = useCallback(() => {
    setData(null);
    clearError();
  }, [clearError]);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    clearError,
  };
};

export default useApi;