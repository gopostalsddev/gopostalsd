import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import theme from './theme';

// Import pages
import AdminPage from './pages/Admin/AdminPage';
import ShopPage from './pages/Shop/ShopPage';

// Import authentication pages
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import EmailVerificationPage from './pages/Auth/EmailVerificationPage';
import ForgotPasswordPage from './pages/Auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/Auth/ResetPasswordPage';
import UnauthorizedPage from './pages/Auth/UnauthorizedPage';

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public routes with layout */}
            <Route path="/" element={<Layout><ShopPage /></Layout>} />
            <Route path="/login" element={<Layout showFooter={false}><LoginPage /></Layout>} />
            <Route path="/register" element={<Layout showFooter={false}><RegisterPage /></Layout>} />
            <Route path="/verify-email" element={<Layout showFooter={false}><EmailVerificationPage /></Layout>} />
            <Route path="/forgot-password" element={<Layout showFooter={false}><ForgotPasswordPage /></Layout>} />
            <Route path="/reset-password" element={<Layout showFooter={false}><ResetPasswordPage /></Layout>} />
            <Route path="/unauthorized" element={<Layout><UnauthorizedPage /></Layout>} />
            
            {/* Protected routes with layout */}
            <Route 
              path="/admin" 
              element={
                <Layout>
                  <ProtectedRoute requireAuth={true} requireRole="Admin">
                    <AdminPage />
                  </ProtectedRoute>
                </Layout>
              } 
            />
            
            {/* Catch-all route for 404 */}
            <Route path="*" element={<Layout><UnauthorizedPage /></Layout>} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
