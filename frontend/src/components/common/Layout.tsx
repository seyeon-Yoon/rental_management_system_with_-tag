import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Container, Paper } from '@mui/material';
import Header from './Header';

const Layout: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: 'grey.50',
      }}
    >
      {/* 헤더 */}
      <Header />

      {/* 메인 콘텐츠 영역 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          py: 3,
        }}
      >
        <Container maxWidth="lg">
          <Paper
            elevation={1}
            sx={{
              minHeight: 'calc(100vh - 120px)',
              bgcolor: 'background.paper',
              borderRadius: 2,
              overflow: 'hidden',
            }}
          >
            {/* 페이지 콘텐츠가 여기에 렌더링됩니다 */}
            <Outlet />
          </Paper>
        </Container>
      </Box>

      {/* 푸터 (선택적) */}
      <Box
        component="footer"
        sx={{
          py: 2,
          px: 2,
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          textAlign: 'center',
          fontSize: '0.875rem',
        }}
      >
        © 2024 융합공과대학 학생회. All rights reserved.
      </Box>
    </Box>
  );
};

export default Layout;