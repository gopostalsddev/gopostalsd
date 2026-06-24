import React, { Suspense, lazy } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Typography, Button } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import theme from './theme';

// Import pages
const AdminPage = lazy(() => import('./pages/Admin/AdminPage'));
const ProductManagementPage = lazy(() => import('./pages/Admin/ProductManagementPage'));
const OrderManagementPage = lazy(() => import('./pages/Admin/OrderManagementPage'));
const ShopPage = lazy(() => import('./pages/Shop/ShopPage'));
const HomePage = lazy(() => import('./pages/Home/HomePage'));
const ContactPage = lazy(() => import('./pages/Contact/ContactPage'));
const CartPage = lazy(() => import('./pages/Cart/CartPage'));
const CheckoutPage = lazy(() => import('./pages/Checkout/CheckoutPage'));
const OrderConfirmationPage = lazy(() => import('./pages/Order/OrderConfirmationPage'));
const AccountPage = lazy(() => import('./pages/Account/AccountPage'));
const TrackOrderPage = lazy(() => import('./pages/TrackOrder/TrackOrderPage'));
const ServicesPage = lazy(() => import('./pages/Services/ServicesPage'));
const FAQsPage = lazy(() => import('./pages/FAQs/FAQsPage'));
const GalleryPage = lazy(() => import('./pages/Gallery/GalleryPage'));
const TermsPage = lazy(() => import('./pages/Legal/TermsPage'));
const PrivacyPage = lazy(() => import('./pages/Legal/PrivacyPage'));
const LoginPage = lazy(() => import('./pages/Auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/Auth/RegisterPage'));
const EmailVerificationPage = lazy(() => import('./pages/Auth/EmailVerificationPage'));
const VerifyEmailPage = lazy(() => import('./pages/Auth/VerifyEmailPage'));
const ForgotPasswordPage = lazy(() => import('./pages/Auth/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/Auth/ResetPasswordPage'));
const UnauthorizedPage = lazy(() => import('./pages/Auth/UnauthorizedPage'));

const RouteLoadingState = () => (
  <Box
    sx={{
      minHeight: '50vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      px: 3,
      textAlign: 'center',
    }}
  >
    <Typography variant="body1" color="text.secondary">
      Loading page...
    </Typography>
  </Box>
);

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <CartProvider>
          <Router>
            <Suspense fallback={<Layout><RouteLoadingState /></Layout>}>
              <Routes>
                {/* Public routes with layout */}
                <Route path="/" element={<Layout><HomePage /></Layout>} />
                <Route path="/shop" element={<Layout><ShopPage /></Layout>} />
                <Route path="/services" element={<Layout><ServicesPage /></Layout>} />
                <Route path="/contact" element={<Layout><ContactPage /></Layout>} />
                <Route path="/faqs" element={<Layout><FAQsPage /></Layout>} />
                <Route path="/gallery" element={<Layout><GalleryPage /></Layout>} />
                <Route path="/cart" element={<Layout><CartPage /></Layout>} />
                <Route path="/checkout" element={<Layout><CheckoutPage /></Layout>} />
                <Route path="/track-order" element={<Layout><TrackOrderPage /></Layout>} />
                <Route path="/terms" element={<Layout><TermsPage /></Layout>} />
                <Route path="/privacy" element={<Layout><PrivacyPage /></Layout>} />
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
                  path="/account"
                  element={
                    <Layout>
                      <ProtectedRoute requireAuth={true}>
                        <AccountPage />
                      </ProtectedRoute>
                    </Layout>
                  }
                />
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
                <Route path="*" element={<Layout><Box sx={{ textAlign: 'center', py: 8 }}><Typography variant="h4">404 - Page Not Found</Typography><Typography variant="body1" sx={{ mb: 3 }}>The page you're looking for doesn't exist.</Typography><Button variant="contained" onClick={() => { window.location.hash = '#/'; }}>Go Home</Button></Box></Layout>} />
              </Routes>
            </Suspense>
          </Router>
        </CartProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
