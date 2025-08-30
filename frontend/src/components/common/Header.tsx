import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  AccountCircle,
  AdminPanelSettings,
  History,
  Logout,
  Home,
  BookOnline,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    handleMenuClose();
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('로그아웃 실패:', error);
      // 에러가 발생해도 로그아웃 처리
      navigate('/login');
    }
    handleMenuClose();
  };

  return (
    <AppBar position="static" sx={{ bgcolor: 'primary.main' }}>
      <Toolbar>
        {/* 로고/타이틀 */}
        <Typography
          variant="h6"
          component="div"
          sx={{ 
            cursor: 'pointer',
            fontWeight: 'bold',
            flexGrow: isMobile ? 1 : 0,
          }}
          onClick={() => navigate('/home')}
        >
          융공대 렌탈시스템
        </Typography>

        {/* 데스크톱 내비게이션 메뉴 */}
        {!isMobile && (
          <Box sx={{ display: 'flex', ml: 4, gap: 1 }}>
            <Button
              color="inherit"
              startIcon={<Home />}
              onClick={() => navigate('/home')}
              sx={{ textTransform: 'none' }}
            >
              품목 목록
            </Button>
            <Button
              color="inherit"
              startIcon={<BookOnline />}
              onClick={() => navigate('/reservations')}
              sx={{ textTransform: 'none' }}
            >
              예약 현황
            </Button>
            <Button
              color="inherit"
              startIcon={<History />}
              onClick={() => navigate('/history')}
              sx={{ textTransform: 'none' }}
            >
              이용 이력
            </Button>
            {user?.role === 'ADMIN' && (
              <Button
                color="inherit"
                startIcon={<AdminPanelSettings />}
                onClick={() => navigate('/admin/dashboard')}
                sx={{ textTransform: 'none' }}
              >
                관리자
              </Button>
            )}
          </Box>
        )}

        <Box sx={{ flexGrow: 1 }} />

        {/* 사용자 정보 및 메뉴 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {!isMobile && (
            <Box sx={{ textAlign: 'right', mr: 1 }}>
              <Typography variant="subtitle2" color="inherit">
                {user?.name}
              </Typography>
              <Typography variant="caption" color="inherit" sx={{ opacity: 0.8 }}>
                {user?.department} • {user?.role === 'ADMIN' ? '관리자' : '학생'}
              </Typography>
            </Box>
          )}
          
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleMenuOpen}
            sx={{ p: 0.5 }}
          >
            <Avatar sx={{ bgcolor: 'secondary.main' }}>
              <AccountCircle />
            </Avatar>
          </IconButton>
        </Box>

        {/* 사용자 메뉴 */}
        <Menu
          id="user-menu"
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          PaperProps={{
            sx: { minWidth: 200 }
          }}
        >
          {/* 사용자 정보 */}
          <Box sx={{ px: 2, py: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold">
              {user?.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.student_id} • {user?.department}
            </Typography>
            <Typography variant="caption" color="primary" display="block">
              {user?.role === 'ADMIN' ? '관리자' : '학생'}
            </Typography>
          </Box>
          
          <Divider />

          {/* 모바일에서만 보이는 내비게이션 메뉴 */}
          {isMobile && (
            <>
              <MenuItem onClick={() => handleNavigation('/home')}>
                <Home sx={{ mr: 2 }} />
                품목 목록
              </MenuItem>
              <MenuItem onClick={() => handleNavigation('/reservations')}>
                <BookOnline sx={{ mr: 2 }} />
                예약 현황
              </MenuItem>
              <MenuItem onClick={() => handleNavigation('/history')}>
                <History sx={{ mr: 2 }} />
                이용 이력
              </MenuItem>
              {user?.role === 'ADMIN' && (
                <MenuItem onClick={() => handleNavigation('/admin/dashboard')}>
                  <AdminPanelSettings sx={{ mr: 2 }} />
                  관리자
                </MenuItem>
              )}
              <Divider />
            </>
          )}

          {/* 로그아웃 */}
          <MenuItem onClick={handleLogout}>
            <Logout sx={{ mr: 2 }} />
            로그아웃
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;