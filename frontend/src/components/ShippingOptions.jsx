import { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Alert,
  CircularProgress,
  Stack
} from '@mui/material';
import {
  LocalShipping as ShippingIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useCartOperations } from '../hooks/useCart';
import { useAuth } from '../contexts/AuthContext';

export function ShippingOptions() {
  const {
    shippingOptions,
    selectedShipping,
    setSelectedShipping,
    calculateShippingOptions
  } = useCartOperations();
  const { user, refreshUser } = useAuth();

  const [calculatingShipping, setCalculatingShipping] = useState(false);
  const [shippingError, setShippingError] = useState(null);

  const handleCalculateShipping = async () => {
    let sourceAddress = user?.shipping_address || user?.address || {};
    const destinationAddress = {
      street: sourceAddress.street || '',
      city: sourceAddress.city || '',
      state: sourceAddress.state || '',
      zip_code: sourceAddress.zip_code || '',
      country: sourceAddress.country || 'US',
      apt: sourceAddress.apt || ''
    };

    const requiredFields = ['street', 'city', 'state', 'zip_code'];
    let missingFields = requiredFields.filter((field) => !destinationAddress[field]);

    // Freshly logged-in sessions can have a stale in-memory user object until profile fetch completes.
    if (missingFields.length > 0) {
      const refreshedUser = await refreshUser();
      sourceAddress = refreshedUser?.shipping_address || refreshedUser?.address || sourceAddress;

      destinationAddress.street = sourceAddress.street || '';
      destinationAddress.city = sourceAddress.city || '';
      destinationAddress.state = sourceAddress.state || '';
      destinationAddress.zip_code = sourceAddress.zip_code || '';
      destinationAddress.country = sourceAddress.country || 'US';
      destinationAddress.apt = sourceAddress.apt || '';
      missingFields = requiredFields.filter((field) => !destinationAddress[field]);
    }

    if (missingFields.length > 0) {
      setShippingError(
        `Missing required fields: ${missingFields.join(', ')}. Add your shipping address in Account or continue to Checkout.`
      );
      return;
    }

    try {
      setCalculatingShipping(true);
      setShippingError(null);
      
      const result = await calculateShippingOptions(destinationAddress);
      
      if (!result.success) {
        setShippingError(result.error);
      }
    } catch {
      setShippingError('Failed to calculate shipping options');
    } finally {
      setCalculatingShipping(false);
    }
  };

  const handleShippingSelection = (event) => {
    const selectedOptionId = parseInt(event.target.value);
    const selectedOption = shippingOptions.find(option => option.id === selectedOptionId);
    setSelectedShipping(selectedOption);
  };

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
        <ShippingIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          Shipping Options
        </Typography>
      </Box>

      {shippingError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {shippingError}
        </Alert>
      )}

      {!shippingOptions || shippingOptions.length === 0 ? (
        <Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Calculate shipping costs for your order
          </Typography>
          <Button
            variant="outlined"
            onClick={handleCalculateShipping}
            disabled={calculatingShipping}
            startIcon={calculatingShipping ? <CircularProgress size={20} /> : <ShippingIcon />}
          >
            {calculatingShipping ? 'Calculating...' : 'Calculate Shipping'}
          </Button>
        </Box>
      ) : (
        <Box>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend">
              Choose Shipping Method
            </FormLabel>
            <RadioGroup
              value={selectedShipping?.id || ''}
              onChange={handleShippingSelection}
            >
              <Stack spacing={1}>
                {shippingOptions.map((option) => (
                  <FormControlLabel
                    key={option.id}
                    value={option.id}
                    control={<Radio />}
                    label={
                      <Box display="flex" justifyContent="space-between" alignItems="center" width="100%">
                        <Box>
                          <Typography variant="body1">
                            {option.method_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {option.carrier_name} • {option.shipping_days} business days
                          </Typography>
                        </Box>
                        <Typography variant="h6" color="primary">
                          ${option.price.toFixed(2)}
                        </Typography>
                      </Box>
                    }
                    sx={{
                      border: '1px solid',
                      borderColor: selectedShipping?.id === option.id ? 'primary.main' : 'grey.300',
                      borderRadius: 1,
                      p: 1,
                      '&:hover': {
                        borderColor: 'primary.main',
                        backgroundColor: 'action.hover'
                      }
                    }}
                  />
                ))}
              </Stack>
            </RadioGroup>
          </FormControl>

          {selectedShipping && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
              <Box display="flex" alignItems="center">
                <CheckIcon sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2" color="success.dark">
                  Selected: {selectedShipping.method_name} - ${selectedShipping.price.toFixed(2)}
                </Typography>
              </Box>
            </Box>
          )}

          <Box sx={{ mt: 2 }}>
            <Button
              variant="outlined"
              size="small"
              onClick={handleCalculateShipping}
              disabled={calculatingShipping}
            >
              Recalculate Shipping
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
}
