import React, { useEffect, useRef, useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Button,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import {
  Payment as PaymentIcon,
  CreditCard as CreditCardIcon
} from '@mui/icons-material';

const PLACEHOLDER_APP_ID = 'sandbox-sq0idb-your-app-id';
const PLACEHOLDER_LOCATION_ID = 'your-location-id';

const getSquareConfig = () => {
  const applicationId = import.meta.env.VITE_SQUARE_APPLICATION_ID;
  const locationId = import.meta.env.VITE_SQUARE_LOCATION_ID;
  return { applicationId, locationId };
};

const isConfigured = ({ applicationId, locationId }) => {
  return Boolean(
    applicationId &&
      locationId &&
      applicationId !== PLACEHOLDER_APP_ID &&
      locationId !== PLACEHOLDER_LOCATION_ID
  );
};

const getSquareSdkUrl = (applicationId) => {
  return applicationId?.startsWith('sandbox-')
    ? 'https://sandbox.web.squarecdn.com/v1/square.js'
    : 'https://web.squarecdn.com/v1/square.js';
};

// Square Web Payments SDK integration
export function SquarePaymentForm({ amount, onPaymentSuccess, processing = false }) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(processing);
  const [cardLoaded, setCardLoaded] = useState(false);
  
  const cardRef = useRef(null);
  const paymentsRef = useRef(null);
  const cardContainerRef = useRef(null);

  useEffect(() => {
    // Wait for DOM to be ready before initializing
    const initSquare = () => {
      const cardContainer = document.getElementById('card-container');
      if (cardContainer) {
        initializeSquare();
      } else {
        // If container not found, try again after a short delay
        setTimeout(initSquare, 50);
      }
    };
    
    // Start initialization after component mounts
    const initTimer = setTimeout(initSquare, 100);
    
    return () => clearTimeout(initTimer);
  }, []);

  const initializeSquare = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const config = getSquareConfig();
      if (!isConfigured(config)) {
        setError(
          'Square payments are not configured for this environment. Set VITE_SQUARE_APPLICATION_ID and VITE_SQUARE_LOCATION_ID in frontend environment variables.'
        );
        setIsLoading(false);
        return;
      }

      // Load Square Web Payments SDK
      if (!window.Square) {
        const script = document.createElement('script');
        script.src = getSquareSdkUrl(config.applicationId);
        script.onload = () => {
          initializeSquarePayments();
        };
        script.onerror = () => {
          setError('Failed to load Square payment SDK');
          setIsLoading(false);
        };
        document.head.appendChild(script);
      } else {
        initializeSquarePayments();
      }
    } catch (error) {
      console.error('Error initializing Square:', error);
      setError('Failed to initialize payment form');
      setIsLoading(false);
    }
  };

  const initializeSquarePayments = async () => {
    try {
      // Check if Square SDK is loaded
      if (!window.Square) {
        throw new Error('Square SDK not loaded');
      }
      
      // Initialize Square payments
      // Get credentials from environment variables (VITE_ prefix required for Vite)
      const config = getSquareConfig();
      if (!isConfigured(config)) {
        throw new Error('Square credentials are not configured.');
      }

      paymentsRef.current = window.Square.payments(config.applicationId, config.locationId);

      // Create card payment method
      cardRef.current = await paymentsRef.current.card();
      
      // Check if card container exists before attaching
      const cardContainer = document.getElementById('card-container');
      if (!cardContainer) {
        throw new Error('Card container element not found');
      }
      
      await cardRef.current.attach('#card-container');
      setCardLoaded(true);
      setIsLoading(false);
    } catch (error) {
      console.error('Error initializing Square payments:', error);
      
      // Provide more specific error message
      if (error.message && error.message.includes('not found')) {
        setError('Card container not found. Please refresh the page.');
      } else {
        setError(`Failed to initialize payment form: ${error.message}`);
      }
      
      setIsLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      setIsProcessing(true);
      setError(null);

      if (!cardRef.current) {
        throw new Error('Payment form not initialized');
      }

      // Tokenize the card
      const result = await cardRef.current.tokenize();
      
      if (result.status === 'OK') {
        // Call the success callback with the token
        await onPaymentSuccess({
          sourceId: result.token,
          paymentMethod: 'card'
        });
      } else if (result.status === 'INVALID_REQUEST_ERROR') {
        throw new Error('Payment request rejected. Verify Square application and location credentials.');
      } else {
        throw new Error(result.errors?.[0]?.detail || 'Payment failed');
      }
    } catch (error) {
      console.error('Payment error:', error);
      setError(error.message || 'Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatAmount = (amountInCents) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amountInCents / 100);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Payment Details
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {isLoading && !error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Initializing payment form...
        </Alert>
      )}

      {/* Payment Amount */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center">
              <PaymentIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">
                Total Amount
              </Typography>
            </Box>
            <Typography variant="h5" color="primary">
              {formatAmount(amount)}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Card Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
            <CreditCardIcon sx={{ mr: 1, color: 'text.secondary' }} />
            <Typography variant="subtitle1">
              Card Information
            </Typography>
          </Box>
          
          <Box
            id="card-container"
            ref={cardContainerRef}
            sx={{
              minHeight: '120px',
              border: '1px solid',
              borderColor: 'grey.300',
              borderRadius: 1,
              p: 2,
              backgroundColor: 'background.paper'
            }}
          >
            {!cardLoaded && isLoading && (
              <Box display="flex" justifyContent="center" alignItems="center" height="100%">
                <CircularProgress size={24} />
                <Typography variant="body2" sx={{ ml: 1 }}>
                  Loading card form...
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Security Notice */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Secure Payment:</strong> Your payment information is encrypted and processed securely by Square. 
          We never store your card details.
        </Typography>
      </Alert>

      {/* Payment Button */}
      <Button
        variant="contained"
        size="large"
        fullWidth
        onClick={handlePayment}
        disabled={!cardLoaded || isProcessing}
        startIcon={isProcessing ? <CircularProgress size={20} /> : <PaymentIcon />}
        sx={{ py: 1.5 }}
      >
        {isProcessing ? 'Processing Payment...' : `Pay ${formatAmount(amount)}`}
      </Button>

      {/* Test Card Information */}
      <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          Test Card Information (Sandbox)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Successful Payment:</strong> 4111 1111 1111 1111<br />
          <strong>Declined Payment:</strong> 4000 0000 0000 0002<br />
          <strong>Expiry:</strong> Any future date<br />
          <strong>CVV:</strong> Any 3 digits
        </Typography>
      </Box>
    </Box>
  );
}

// Alternative implementation using Square's hosted payment page
export function SquareHostedPaymentForm({ amount, onPaymentSuccess }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleHostedPayment = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // This would typically redirect to Square's hosted payment page
      // For now, we'll simulate the process
      const response = await fetch('/api/payments/create-hosted-payment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: amount,
          currency: 'USD'
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to Square's hosted payment page
        window.location.href = data.payment_url;
      } else {
        throw new Error('Failed to create hosted payment');
      }
    } catch (error) {
      console.error('Hosted payment error:', error);
      setError(error.message || 'Failed to create payment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Secure Payment
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          You will be redirected to Square's secure payment page to complete your purchase.
        </Typography>
      </Alert>

      <Button
        variant="contained"
        size="large"
        fullWidth
        onClick={handleHostedPayment}
        disabled={isLoading}
        startIcon={isLoading ? <CircularProgress size={20} /> : <PaymentIcon />}
        sx={{ py: 1.5 }}
      >
        {isLoading ? 'Creating Payment...' : 'Continue to Payment'}
      </Button>
    </Box>
  );
}
