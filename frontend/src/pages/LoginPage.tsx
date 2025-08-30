import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  AccountCircle,
  School,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [formData, setFormData] = useState({
    studentId: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 로그인 성공 후 리다이렉트 경로
  const from = (location.state as any)?.from?.pathname || '/home';

  const handleInputChange = (field: 'studentId' | 'password') => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    // 입력 시 에러 메시지 클리어
    if (error) setError(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    // 기본 유효성 검사
    if (!formData.studentId.trim() || !formData.password.trim()) {
      setError('학번과 비밀번호를 모두 입력해주세요.');
      setIsLoading(false);
      return;
    }

    try {
      await login(formData.studentId, formData.password);
      // 로그인 성공 시 원래 가려던 페이지로 이동
      navigate(from, { replace: true });
    } catch (error: any) {
      console.error('로그인 실패:', error);
      setError(
        error.message || '로그인에 실패했습니다. 학번과 비밀번호를 확인해주세요.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={8}
          sx={{
            p: 4,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {/* 헤더 */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <School sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
              융공대 렌탈시스템
            </Typography>
            <Typography variant="body1" color="text.secondary">
              융합공과대학 학생회 대여 서비스
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {/* 로그인 폼 */}
          <Box component="form" onSubmit={handleSubmit}>
            {/* 에러 메시지 */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* 학번 입력 */}
            <TextField
              fullWidth
              label="학번"
              variant="outlined"
              value={formData.studentId}
              onChange={handleInputChange('studentId')}
              disabled={isLoading}
              placeholder="예: 20230001"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AccountCircle />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
              autoComplete="username"
            />

            {/* 비밀번호 입력 */}
            <TextField
              fullWidth
              label="비밀번호"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              value={formData.password}
              onChange={handleInputChange('password')}
              disabled={isLoading}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={togglePasswordVisibility}
                      onMouseDown={(e) => e.preventDefault()}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 4 }}
              autoComplete="current-password"
            />

            {/* 로그인 버튼 */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoading}
              sx={{
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 'bold',
                textTransform: 'none',
              }}
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </Button>
          </Box>

          {/* 안내 메시지 */}
          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              대학교 통합정보시스템의 학번과 비밀번호로 로그인하세요
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              융합공과대학 재학생만 이용 가능합니다
            </Typography>
          </Box>

          {/* 추가 정보 */}
          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <strong>이용 안내:</strong>
            </Typography>
            <Typography variant="caption" color="text.secondary" component="ul" sx={{ pl: 2, m: 0 }}>
              <li>예약 후 1시간 내 학생회실 방문</li>
              <li>최대 7일 대여 (연장 가능)</li>
              <li>분실 시 변상 의무</li>
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;