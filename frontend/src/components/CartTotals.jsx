import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Divider,
  Stack
} from '@mui/material';
import { useCartFormatting } from '../hooks/useCart';

export function CartTotals({ cart }) {
  const { formatCartTotals } = useCartFormatting();
  const totals = formatCartTotals();

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Order Summary
      </Typography>
      
      <Divider sx={{ my: 2 }} />
      
      <Stack spacing={2}>
        {/* Subtotal */}
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">
            Subtotal
          </Typography>
          <Typography variant="body1">
            {totals.subtotal}
          </Typography>
        </Box>

        {/* Shipping */}
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">
            Shipping
          </Typography>
          <Typography variant="body1">
            {cart.shipping_cost > 0 ? totals.shipping : 'Calculated at checkout'}
          </Typography>
        </Box>

        {/* Tax */}
        <Box display="flex" justifyContent="space-between">
          <Typography variant="body1">
            Tax
          </Typography>
          <Typography variant="body1">
            {totals.tax}
          </Typography>
        </Box>

        <Divider />

        {/* Total */}
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">
            Total
          </Typography>
          <Typography variant="h6" color="primary">
            {totals.total}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
}
