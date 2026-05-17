import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Typography, Button } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import theme from './theme';

// Import pages
import AdminPage from './pages/Admin/AdminPage';
import ProductManagementPage from './pages/Admin/ProductManagementPage';
import OrderManagementPage from './pages/Admin/OrderManagementPage';
import ShopPage from './pages/Shop/ShopPage';
import HomePage from './pages/Home/HomePage';
import ContactPage from './pages/Contact/ContactPage';
import CartPage from './pages/Cart/CartPage';
import CheckoutPage from './pages/Checkout/CheckoutPage';
import OrderConfirmationPage from './pages/Order/OrderConfirmationPage';

// Import authentication pages
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import EmailVerificationPage from './pages/Auth/EmailVerificationPage';
import VerifyEmailPage from './pages/Auth/VerifyEmailPage';
import ForgotPasswordPage from './pages/Auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/Auth/ResetPasswordPage';
import UnauthorizedPage from './pages/Auth/UnauthorizedPage';

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <CartProvider>
          <Router>
            <Routes>
              {/* Public routes with layout */}
              <Route path="/" element={<Layout><HomePage /></Layout>} />
              <Route path="/shop" element={<Layout><ShopPage /></Layout>} />
              <Route path="/contact" element={<Layout><ContactPage /></Layout>} />
              <Route path="/cart" element={<Layout><CartPage /></Layout>} />
              <Route path="/checkout" element={<Layout><CheckoutPage /></Layout>} />
              <Route path="/order-confirmation" element={<Layout><OrderConfirmationPage /></Layout>} />
              <Route path="/login" element={<Layout showFooter={false}><LoginPage /></Layout>} />
              <Route path="/register" element={<Layout showFooter={false}><RegisterPage /></Layout>} />
              <Route path="/verify-email" element={<Layout showFooter={false}><EmailVerificationPage /></Layout>} />
              <Route path="/verify" element={<Layout showFooter={false}><VerifyEmailPage /></Layout>} />
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
              <Route
                path="/admin/products"
                element={
                  <Layout>
                    <ProtectedRoute requireAuth={true} requireRole="Admin">
                      <ProductManagementPage />
                    </ProtectedRoute>
                  </Layout>
                }
              />
              <Route
                path="/admin/orders"
                element={
                  <Layout>
                    <ProtectedRoute requireAuth={true} requireRole="Admin">
                      <OrderManagementPage />
                    </ProtectedRoute>
                  </Layout>
                }
              />
              
              {/* Catch-all route for 404 */}
              <Route path="*" element={<Layout><Box sx={{ textAlign: 'center', py: 8 }}><Typography variant="h4">404 - Page Not Found</Typography><Typography variant="body1" sx={{ mb: 3 }}>The page you're looking for doesn't exist.</Typography><Button variant="contained" onClick={() => window.location.href = '/'}>Go Home</Button></Box></Layout>} />
            </Routes>
          </Router>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
