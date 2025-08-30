import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Box } from '@mui/material';

import Layout from '@/components/common/Layout';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import LoginPage from '@/pages/LoginPage';
import HomePage from '@/pages/HomePage';
import ReservationPage from '@/pages/ReservationPage';
import RentalHistoryPage from '@/pages/RentalHistoryPage';
import AdminDashboard from '@/pages/admin/AdminDashboard';
import ItemManagement from '@/pages/admin/ItemManagement';
import RentalManagement from '@/pages/admin/RentalManagement';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<LoginPage />} />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="reservations" element={<ReservationPage />} />
          <Route path="history" element={<RentalHistoryPage />} />
          
          {/* Admin Routes */}
          <Route path="admin" element={<ProtectedRoute requireAdmin><Outlet /></ProtectedRoute>}>
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="items" element={<ItemManagement />} />
            <Route path="rentals" element={<RentalManagement />} />
          </Route>
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </Box>
  );
}

export default App;