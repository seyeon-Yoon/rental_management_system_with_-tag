import React from 'react';
import {
  Snackbar,
  Alert,
  Stack,
} from '@mui/material';
import { useToast, Toast } from '@/hooks';

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onClose }) => {
  return (
    <Stack spacing={1}>
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open={true}
          autoHideDuration={toast.autoHideDuration}
          onClose={() => onClose(toast.id)}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <Alert
            onClose={() => onClose(toast.id)}
            severity={toast.severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </Stack>
  );
};

export default ToastContainer;