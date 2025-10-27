import React, { useState } from 'react';
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
  Stack,
  Chip
} from '@mui/material';
import {
  LocalShipping as ShippingIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useCartOperations } from '../hooks/useCart';

export function ShippingOptions() {
  const {
    shippingOptions,
    selectedShipping,
    setSelectedShipping,
    calculateShippingOptions,
    loading
  } = useCartOperations();

  const [calculatingShipping, setCalculatingShipping] = useState(false);
  const [shippingError, setShippingError] = useState(null);

  const handleCalculateShipping = async () => {
    // Use default address for now (will be replaced with actual destination from cart)
    const defaultAddress = {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'US'
    };

    try {
      setCalculatingShipping(true);
      setShippingError(null);
      
      const result = await calculateShippingOptions(defaultAddress);
      
      if (!result.success) {
        setShippingError(result.error);
      }
    } catch (error) {
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
