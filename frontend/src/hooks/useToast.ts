import { useState, useCallback } from 'react';
import { AlertColor } from '@mui/material/Alert';

export interface Toast {
  id: string;
  message: string;
  severity: AlertColor;
  autoHideDuration?: number;
}

export interface UseToastReturn {
  toasts: Toast[];
  showToast: (message: string, severity?: AlertColor, autoHideDuration?: number) => void;
  hideToast: (id: string) => void;
  clearAllToasts: () => void;
}

export const useToast = (): UseToastReturn => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((
    message: string, 
    severity: AlertColor = 'info', 
    autoHideDuration = 4000
  ) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: Toast = {
      id,
      message,
      severity,
      autoHideDuration,
    };

    setToasts(prev => [...prev, newToast]);

    // Auto hide
    if (autoHideDuration > 0) {
      setTimeout(() => {
        hideToast(id);
      }, autoHideDuration);
    }
  }, []);

  const hideToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  return {
    toasts,
    showToast,
    hideToast,
    clearAllToasts,
  };
};

export default useToast;