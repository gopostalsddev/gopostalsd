import React from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Divider,
  Stack,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  ShoppingCart as CartIcon,
  LocalShipping as ShippingIcon,
  Payment as PaymentIcon
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

export default function OrderConfirmationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get order data from location state or URL params
  const orderData = location.state?.orderData || null;

  if (!orderData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Order Not Found
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            We couldn't find the order information. Please check your email for confirmation details.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Return Home
          </Button>
        </Paper>
      </Container>
    );
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'processing':
        return 'info';
      case 'shipped':
        return 'primary';
      case 'delivered':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Success Header */}
      <Box textAlign="center" sx={{ mb: 4 }}>
        <CheckIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
        <Typography variant="h3" gutterBottom>
          Order Confirmed!
        </Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>
          Order #{orderData.order_number}
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          Thank you for your order. You will receive a confirmation email shortly.
        </Typography>
      </Box>

      <Box display="flex" flexDirection={{ xs: 'column', lg: 'row' }} gap={4}>
        {/* Order Details */}
        <Box flex={2}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Order Details
            </Typography>
            
            <Divider sx={{ my: 2 }} />

            {/* Order Status */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Order Status
              </Typography>
              <Chip
                label={orderData.status.charAt(0).toUpperCase() + orderData.status.slice(1)}
                color={getStatusColor(orderData.status)}
                variant="outlined"
              />
            </Box>

            {/* Customer Information */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Customer Information
              </Typography>
              <Typography variant="body1">
                {orderData.customer_first_name} {orderData.customer_last_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {orderData.customer_email}
              </Typography>
              {orderData.customer_phone && (
                <Typography variant="body2" color="text.secondary">
                  {orderData.customer_phone}
                </Typography>
              )}
            </Box>

            {/* Shipping Address */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Shipping Address
              </Typography>
              <Typography variant="body2">
                {orderData.shipping_address.street}
                {orderData.shipping_address.apt && `, ${orderData.shipping_address.apt}`}
              </Typography>
              <Typography variant="body2">
                {orderData.shipping_address.city}, {orderData.shipping_address.state} {orderData.shipping_address.zip_code}
              </Typography>
              <Typography variant="body2">
                {orderData.shipping_address.country}
              </Typography>
            </Box>

            {/* Payment Information */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Payment Information
              </Typography>
              <Typography variant="body2">
                Payment Status: <Chip label={orderData.payment_status} color="success" size="small" />
              </Typography>
              <Typography variant="body2">
                Payment Method: {orderData.payment_method || 'Card'}
              </Typography>
              {orderData.payment_provider && (
                <Typography variant="body2">
                  Processed by: {orderData.payment_provider}
                </Typography>
              )}
            </Box>

            {/* Tracking Information */}
            {orderData.tracking_number && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Tracking Information
                </Typography>
                <Typography variant="body2">
                  Tracking Number: {orderData.tracking_number}
                </Typography>
                {orderData.carrier_name && (
                  <Typography variant="body2">
                    Carrier: {orderData.carrier_name}
                  </Typography>
                )}
              </Box>
            )}
          </Paper>
        </Box>

        {/* Order Summary */}
        <Box flex={1}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Order Summary
            </Typography>
            
            <Divider sx={{ my: 2 }} />

            {/* Order Items */}
            <Stack spacing={2} sx={{ mb: 3 }}>
              {orderData.items.map((item) => (
                <Box key={item.id} display="flex" justifyContent="space-between">
                  <Box>
                    <Typography variant="body1">{item.product_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Qty: {item.quantity}
                    </Typography>
                  </Box>
                  <Typography variant="body1">
                    {formatPrice(item.total_price)}
                  </Typography>
                </Box>
              ))}
            </Stack>

            <Divider sx={{ my: 2 }} />

            {/* Totals */}
            <Stack spacing={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1">Subtotal</Typography>
                <Typography variant="body1">{formatPrice(orderData.subtotal)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1">Shipping</Typography>
                <Typography variant="body1">{formatPrice(orderData.shipping_cost)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body1">Tax</Typography>
                <Typography variant="body1">{formatPrice(orderData.tax_amount)}</Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">Total</Typography>
                <Typography variant="h6" color="primary">
                  {formatPrice(orderData.total_amount)}
                </Typography>
              </Box>
            </Stack>
          </Paper>

          {/* Action Buttons */}
          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={() => navigate('/')}
              sx={{ mb: 2 }}
            >
              Continue Shopping
            </Button>
            <Button
              variant="outlined"
              size="large"
              fullWidth
              onClick={() => navigate('/contact')}
            >
              Contact Support
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}
