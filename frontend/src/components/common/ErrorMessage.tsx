import React from 'react';
import { Alert, AlertTitle, Box } from '@mui/material';

interface ErrorMessageProps {
  title?: string;
  message: string;
  severity?: 'error' | 'warning' | 'info';
  variant?: 'standard' | 'filled' | 'outlined';
  onRetry?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  title,
  message,
  severity = 'error',
  variant = 'standard',
  onRetry,
}) => {
  return (
    <Box sx={{ p: 2 }}>
      <Alert 
        severity={severity} 
        variant={variant}
        action={
          onRetry && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <button onClick={onRetry}>다시 시도</button>
            </Box>
          )
        }
      >
        {title && <AlertTitle>{title}</AlertTitle>}
        {message}
      </Alert>
    </Box>
  );
};

export default ErrorMessage;