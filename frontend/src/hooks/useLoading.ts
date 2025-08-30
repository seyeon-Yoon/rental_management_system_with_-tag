import { useState, useCallback } from 'react';

export interface UseLoadingReturn {
  loading: boolean;
  setLoading: (loading: boolean) => void;
  withLoading: <T>(asyncFn: () => Promise<T>) => Promise<T>;
}

export const useLoading = (initialLoading = false): UseLoadingReturn => {
  const [loading, setLoading] = useState(initialLoading);

  const withLoading = useCallback(async <T>(asyncFn: () => Promise<T>): Promise<T> => {
    try {
      setLoading(true);
      const result = await asyncFn();
      return result;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    setLoading,
    withLoading,
  };
};

export default useLoading;