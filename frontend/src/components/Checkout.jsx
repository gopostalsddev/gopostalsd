import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  Divider,
  Stack,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Card,
  CardContent
} from '@mui/material';
import {
  ShoppingCart as CartIcon,
  Payment as PaymentIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useCartOperations, useCartFormatting } from '../hooks/useCart';
import { SquarePaymentForm } from './SquarePaymentForm';
import { api } from '../services/api';

const steps = ['Cart Review', 'Shipping & Billing', 'Payment', 'Confirmation'];

export function Checkout() {
  const {
    cart,
    loading,
    error,
    selectedShipping,
    calculateShippingOptions,
    getCartStats
  } = useCartOperations();

  const { formatPrice, formatCartTotals } = useCartFormatting();

  const [activeStep, setActiveStep] = useState(0);
  const [checkoutData, setCheckoutData] = useState({
    shippingAddress: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'US',
      apt: ''
    },
    billingAddress: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'US',
      apt: ''
    },
    customerInfo: {
      email: '',
      first_name: '',
      last_name: '',
      phone: ''
    },
    useSameAddress: true
  });
  const [orderResult, setOrderResult] = useState(null);
  const [processingOrder, setProcessingOrder] = useState(false);

  const cartStats = getCartStats();

  useEffect(() => {
    if (cartStats.isEmpty) {
      // Redirect to cart if empty
      window.location.href = '/cart';
    }
  }, [cartStats.isEmpty]);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleInputChange = (section, field, value) => {
    setCheckoutData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleSameAddressChange = (event) => {
    const useSameAddress = event.target.checked;
    setCheckoutData(prev => ({
      ...prev,
      useSameAddress,
      billingAddress: useSameAddress ? prev.shippingAddress : prev.billingAddress
    }));
  };

  const handleCalculateShipping = async () => {
    const result = await calculateShippingOptions(checkoutData.shippingAddress);
    if (result.success) {
      handleNext();
    }
  };

  const handleCreateOrder = async (paymentData) => {
    try {
      setProcessingOrder(true);

      // Create order
      const orderResponse = await api.post('/orders/', {
        customer_info: checkoutData.customerInfo,
        shipping_address: checkoutData.shippingAddress,
        billing_address: checkoutData.useSameAddress ? 
          checkoutData.shippingAddress : 
          checkoutData.billingAddress
      });

      const orderData = orderResponse.data;

      // Process payment
      const paymentResponse = await api.post(`/orders/${orderData.id}/payment`, {
        source_id: paymentData.sourceId,
        payment_method: 'card'
      });

      const paymentResult = paymentResponse.data;

      if (paymentResult.success) {
        setOrderResult(paymentResult);
        setActiveStep(3); // Go to confirmation
      } else {
        throw new Error(paymentResult.error);
      }
    } catch (error) {
      console.error('Order processing error:', error);
      alert('Failed to process order: ' + error.message);
    } finally {
      setProcessingOrder(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return <CartReviewStep cart={cart} />;
      case 1:
        return (
          <ShippingBillingStep
            checkoutData={checkoutData}
            onInputChange={handleInputChange}
            onSameAddressChange={handleSameAddressChange}
            selectedShipping={selectedShipping}
          />
        );
      case 2:
        return (
          <PaymentStep
            cart={cart}
            checkoutData={checkoutData}
            onCreateOrder={handleCreateOrder}
            processing={processingOrder}
          />
        );
      case 3:
        return <ConfirmationStep orderResult={orderResult} />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading checkout...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Checkout
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper elevation={2} sx={{ p: 4 }}>
        {renderStepContent(activeStep)}
      </Paper>

      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          color="inherit"
          disabled={activeStep === 0}
          onClick={handleBack}
          sx={{ mr: 1 }}
        >
          Back
        </Button>
        <Box sx={{ flex: '1 1 auto' }} />
        
        {activeStep === 0 && (
          <Button onClick={handleCalculateShipping}>
            Calculate Shipping
          </Button>
        )}
        
        {activeStep === 1 && (
          <Button onClick={handleNext}>
            Continue to Payment
          </Button>
        )}
      </Box>
    </Container>
  );
}

// Step Components
function CartReviewStep({ cart }) {
  const { formatCartTotals } = useCartFormatting();
  const totals = formatCartTotals();

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Your Order
      </Typography>
      
      <Stack spacing={2}>
        {cart.items.map((item) => (
          <Box key={item.id} display="flex" justifyContent="space-between" alignItems="center">
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

      <Box display="flex" justifyContent="space-between">
        <Typography variant="h6">Total</Typography>
        <Typography variant="h6" color="primary">
          {totals.total}
        </Typography>
      </Box>
    </Box>
  );
}

function ShippingBillingStep({ checkoutData, onInputChange, onSameAddressChange, selectedShipping }) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Shipping & Billing Information
      </Typography>

      <Stack spacing={3}>
        {/* Customer Information */}
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Contact Information
          </Typography>
          <Stack direction="row" spacing={2}>
            <TextField
              label="First Name"
              value={checkoutData.customerInfo.first_name}
              onChange={(e) => onInputChange('customerInfo', 'first_name', e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Last Name"
              value={checkoutData.customerInfo.last_name}
              onChange={(e) => onInputChange('customerInfo', 'last_name', e.target.value)}
              required
              fullWidth
            />
          </Stack>
          <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
            <TextField
              label="Email"
              type="email"
              value={checkoutData.customerInfo.email}
              onChange={(e) => onInputChange('customerInfo', 'email', e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Phone"
              value={checkoutData.customerInfo.phone}
              onChange={(e) => onInputChange('customerInfo', 'phone', e.target.value)}
              fullWidth
            />
          </Stack>
        </Box>

        {/* Shipping Address */}
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Shipping Address
          </Typography>
          <TextField
            label="Street Address"
            value={checkoutData.shippingAddress.street}
            onChange={(e) => onInputChange('shippingAddress', 'street', e.target.value)}
            required
            fullWidth
            sx={{ mb: 2 }}
          />
          <Stack direction="row" spacing={2}>
            <TextField
              label="City"
              value={checkoutData.shippingAddress.city}
              onChange={(e) => onInputChange('shippingAddress', 'city', e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="State"
              value={checkoutData.shippingAddress.state}
              onChange={(e) => onInputChange('shippingAddress', 'state', e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="ZIP Code"
              value={checkoutData.shippingAddress.zip_code}
              onChange={(e) => onInputChange('shippingAddress', 'zip_code', e.target.value)}
              required
              fullWidth
            />
          </Stack>
        </Box>

        {/* Billing Address */}
        <Box>
          <FormControlLabel
            control={
              <Radio
                checked={checkoutData.useSameAddress}
                onChange={onSameAddressChange}
              />
            }
            label="Use same address for billing"
          />
        </Box>
      </Stack>
    </Box>
  );
}

function PaymentStep({ cart, checkoutData, onCreateOrder, processing }) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Payment Information
      </Typography>
      
      <SquarePaymentForm
        amount={cart.total * 100} // Convert to cents
        onPaymentSuccess={onCreateOrder}
        processing={processing}
      />
    </Box>
  );
}

function ConfirmationStep({ orderResult }) {
  if (!orderResult) {
    return (
      <Box textAlign="center">
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Processing your order...
        </Typography>
      </Box>
    );
  }

  return (
    <Box textAlign="center">
      <CheckIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
      <Typography variant="h4" gutterBottom>
        Order Confirmed!
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Order #{orderResult.order.order_number}
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>
        Thank you for your order. You will receive a confirmation email shortly.
      </Typography>
      <Button variant="contained" size="large" href="/">
        Continue Shopping
      </Button>
    </Box>
  );
}
