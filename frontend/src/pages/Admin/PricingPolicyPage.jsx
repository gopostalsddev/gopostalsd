import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import TrendingUpOutlinedIcon from '@mui/icons-material/TrendingUpOutlined';
import { fetchPricingPolicy, updatePricingPolicy } from '../../services/product_service';

const fieldLabels = {
  cad_to_usd_rate: 'CAD to USD Rate',
  exchange_buffer_percent: 'FX Buffer %',
  markup_percent: 'Markup %',
  fixed_fee_usd: 'Fixed Fee USD',
  minimum_profit_usd: 'Minimum Profit USD',
  rounding_increment: 'Rounding Increment',
  customization_file_review_fee_usd: 'File Review Fee USD',
  customization_design_assist_fee_usd: 'Design Assist Fee USD',
};

const PricingPolicyPage = () => {
  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPolicy = async () => {
      try {
        setLoading(true);
        const data = await fetchPricingPolicy();
        setPolicy(data);
      } catch (err) {
        setError('Failed to load pricing policy');
      } finally {
        setLoading(false);
      }
    };

    loadPolicy();
  }, []);

  const handleChange = (field, value) => {
    setPolicy((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setMessage('');
      const updated = await updatePricingPolicy(policy);
      setPolicy(updated);
      setMessage('Pricing policy updated successfully. New prices will use these rules.');
    } catch (err) {
      setError(err.message || 'Failed to update pricing policy');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !policy) {
    return (
      <Box sx={{ maxWidth: '1100px', mx: 'auto', px: { xs: 3, md: 6 }, py: { xs: 4, md: 6 } }}>
        <Typography variant="h5">Loading pricing policy...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flex: 1, backgroundColor: (theme) => theme.palette.grey[50], py: { xs: 4, md: 6 } }}>
      <Box sx={{ maxWidth: '1100px', mx: 'auto', px: { xs: 3, md: 6 } }}>
        <Stack spacing={4}>
          <Box>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Pricing Policy
            </Typography>
            <Typography variant="body1" color="text.secondary">
              This page controls how supplier cost becomes storefront price. The owner can protect margin against exchange-rate movement, apply markup consistently, and charge for customization work.
            </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}
          {message && <Alert severity="success">{message}</Alert>}

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 7 }}>
              <Paper sx={{ p: 3, borderRadius: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Pricing Controls
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(fieldLabels).map(([field, label]) => (
                    <Grid key={field} size={{ xs: 12, sm: 6 }}>
                      <TextField
                        fullWidth
                        label={label}
                        type="number"
                        value={policy[field] ?? ''}
                        onChange={(e) => handleChange(field, e.target.value)}
                        inputProps={{ step: '0.01' }}
                      />
                    </Grid>
                  ))}
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button variant="contained" onClick={handleSave} disabled={saving}>
                    {saving ? 'Saving...' : 'Save Pricing Policy'}
                  </Button>
                </Box>
              </Paper>
            </Grid>

            <Grid size={{ xs: 12, md: 5 }}>
              <Paper sx={{ p: 3, borderRadius: 3, height: '100%' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <TrendingUpOutlinedIcon color="primary" />
                  <Typography variant="h6">What these settings do</Typography>
                </Box>
                <Stack spacing={2}>
                  <Typography variant="body2" color="text.secondary">
                    CAD to USD Rate: converts the supplier's Canadian-dollar cost into US dollars.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    FX Buffer %: adds safety margin before markup so exchange-rate changes do not erase profit.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Markup %: applies the target retail margin after conversion and protection buffer.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Fixed Fee and Minimum Profit: ensure each order covers overhead and does not fall below a minimum dollar return.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Customization Fees: add service charges when clients ask for file review or design assistance.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Rounding Increment: rounds final price up to a cleaner retail number such as $0.05 increments.
                  </Typography>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Stack>
      </Box>
    </Box>
  );
};

export default PricingPolicyPage;
