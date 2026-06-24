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
  Checkbox,
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
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const steps = ['Cart Review', 'Shipping & Billing', 'Payment', 'Confirmation'];

export function Checkout() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  
  const {
    cart,
    loading,
    error,
    selectedShipping,
    calculateShippingOptions,
    clearEntireCart,
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

  // Populate addresses from user data when component mounts
  useEffect(() => {
    if (user) {
      // Get shipping address (default to shipping_address if available, fallback to address)
      const userShippingAddress = user.shipping_address || user.address || {};
      
      // Get billing address
      const userBillingAddress = user.billing_address || {};
      
      setCheckoutData(prev => ({
        ...prev,
        shippingAddress: {
          street: userShippingAddress.street || '',
          city: userShippingAddress.city || '',
          state: userShippingAddress.state || '',
          zip_code: userShippingAddress.zip_code || '',
          country: userShippingAddress.country || 'US',
          apt: userShippingAddress.apt || ''
        },
        billingAddress: userBillingAddress.street ? {
          street: userBillingAddress.street || '',
          city: userBillingAddress.city || '',
          state: userBillingAddress.state || '',
          zip_code: userBillingAddress.zip_code || '',
          country: userBillingAddress.country || 'US',
          apt: userBillingAddress.apt || ''
        } : {
          street: userShippingAddress.street || '',
          city: userShippingAddress.city || '',
          state: userShippingAddress.state || '',
          zip_code: userShippingAddress.zip_code || '',
          country: userShippingAddress.country || 'US',
          apt: userShippingAddress.apt || ''
        },
        customerInfo: {
          email: user.email || '',
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          phone: user.phone || ''
        }
      }));
    }
  }, [user]);
  const [orderResult, setOrderResult] = useState(null);
  const [processingOrder, setProcessingOrder] = useState(false);
  const [checkoutStepError, setCheckoutStepError] = useState(null);

  const cartStats = getCartStats();

  const getCheckoutSessionId = () => {
    const existingSessionId =
      cart.session_id ||
      sessionStorage.getItem('cart_session_id') ||
      localStorage.getItem('cart_session_id');
    if (existingSessionId) {
      sessionStorage.setItem('cart_session_id', existingSessionId);
      localStorage.setItem('cart_session_id', existingSessionId);
      return existingSessionId;
    }

    const generatedSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('cart_session_id', generatedSessionId);
    localStorage.setItem('cart_session_id', generatedSessionId);
    return generatedSessionId;
  };
  
  useEffect(() => {
    // Wait for authentication
    if (!isAuthenticated) {
      return;
    }
    
    // Wait for cart to finish loading (check if cart has an ID or if items array is defined)
    if (loading) {
      return;
    }
    
    // If cart has no ID yet and is still empty, it means it hasn't loaded yet
    if (!cart.id && cartStats.isEmpty) {
      return;
    }
    
    // Only redirect if cart is truly empty AND has been loaded (has an ID)
    if (cart.id && cartStats.isEmpty) {
      navigate('/cart');
    }
  }, [cartStats.isEmpty, loading, isAuthenticated, cartStats.itemCount, cart.items, cart.id, navigate]);

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
      billingAddress: useSameAddress ? { ...prev.shippingAddress } : prev.billingAddress
    }));
  };

  const handleCalculateShipping = async () => {
    setCheckoutStepError(null);
    const result = await calculateShippingOptions(checkoutData.shippingAddress);
    if (result.success) {
      handleNext();
    } else {
      setCheckoutStepError(result.error || 'Unable to calculate shipping. Please review your address and try again.');
    }
  };

  const handleCreateOrder = async (paymentData) => {
    try {
      setProcessingOrder(true);

      // Validate required fields
      const requiredCustomerFields = ['email', 'first_name', 'last_name'];
      for (const field of requiredCustomerFields) {
        if (!checkoutData.customerInfo[field] || checkoutData.customerInfo[field].trim() === '') {
          throw new Error(`Please fill in your ${field.replace('_', ' ')} before proceeding`);
        }
      }

      const requiredAddressFields = ['street', 'city', 'state', 'zip_code', 'country'];
      for (const field of requiredAddressFields) {
        if (!checkoutData.shippingAddress[field] || checkoutData.shippingAddress[field].trim() === '') {
          throw new Error(`Please complete your shipping address (${field})`);
        }
      }

      // Get session ID for the cart
      const sessionId = getCheckoutSessionId();
      
      // Create order
      const orderResponse = await api.post(`/orders/?session_id=${sessionId}`, {
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
        const clearResult = await clearEntireCart();
        if (!clearResult.success) {
          // Do not fail checkout confirmation if cart clear fails.
          console.warn('Order completed but cart clear failed:', clearResult.error);
        }
        setOrderResult(paymentResult);
        setActiveStep(3); // Go to confirmation
      } else {
        throw new Error(paymentResult.error);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message || 'Failed to process order';
      alert('Failed to process order: ' + errorMessage);
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
            amountCents={Math.max(0, Math.round((Number(cartStats.total) || 0) * 100))}
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

  // Check authentication - show loading while redirecting
  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Redirecting to login...
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
        {checkoutStepError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {checkoutStepError}
          </Alert>
        )}
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
          <Button onClick={handleNext}>
            Continue to Shipping
          </Button>
        )}
        
        {activeStep === 1 && (
          <Button onClick={handleCalculateShipping}>
            Calculate Shipping & Continue to Payment
          </Button>
        )}
      </Box>
    </Container>
  );
}

// Step Components
function CartReviewStep({ cart }) {
  const { formatCartTotals, formatPrice } = useCartFormatting();
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

      <Stack spacing={1}>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">Subtotal</Typography>
          <Typography variant="body1">{totals.subtotal}</Typography>
        </Box>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">Shipping</Typography>
          <Typography variant="body1">{totals.shipping}</Typography>
        </Box>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">Tax</Typography>
          <Typography variant="body1">{totals.tax}</Typography>
        </Box>
        <Divider sx={{ my: 1 }} />
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">Total</Typography>
          <Typography variant="h6" color="primary">
            {totals.total}
          </Typography>
        </Box>
      </Stack>
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
          <TextField
            label="Apartment/Suite (Optional)"
            value={checkoutData.shippingAddress.apt}
            onChange={(e) => onInputChange('shippingAddress', 'apt', e.target.value)}
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
              <Checkbox
                checked={checkoutData.useSameAddress}
                onChange={onSameAddressChange}
              />
            }
            label="Use same address for billing"
          />
          {!checkoutData.useSameAddress && (
            <>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
                Billing Address
              </Typography>
              <TextField
                label="Street Address"
                value={checkoutData.billingAddress.street}
                onChange={(e) => onInputChange('billingAddress', 'street', e.target.value)}
                required={!checkoutData.useSameAddress}
                fullWidth
                sx={{ mb: 2 }}
              />
              <TextField
                label="Apartment/Suite (Optional)"
                value={checkoutData.billingAddress.apt}
                onChange={(e) => onInputChange('billingAddress', 'apt', e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Stack direction="row" spacing={2}>
                <TextField
                  label="City"
                  value={checkoutData.billingAddress.city}
                  onChange={(e) => onInputChange('billingAddress', 'city', e.target.value)}
                  required={!checkoutData.useSameAddress}
                  fullWidth
                />
                <TextField
                  label="State"
                  value={checkoutData.billingAddress.state}
                  onChange={(e) => onInputChange('billingAddress', 'state', e.target.value)}
                  required={!checkoutData.useSameAddress}
                  fullWidth
                />
                <TextField
                  label="ZIP Code"
                  value={checkoutData.billingAddress.zip_code}
                  onChange={(e) => onInputChange('billingAddress', 'zip_code', e.target.value)}
                  required={!checkoutData.useSameAddress}
                  fullWidth
                />
              </Stack>
            </>
          )}
        </Box>
      </Stack>
    </Box>
  );
}

function PaymentStep({ amountCents, checkoutData, onCreateOrder, processing }) {
  const amount = Number.isFinite(Number(amountCents)) ? Number(amountCents) : 0;

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Payment Information
      </Typography>
      
      <SquarePaymentForm
        amount={amount} // Convert to cents
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
