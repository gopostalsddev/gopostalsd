import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  Paper,
  Stack,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import SearchIcon from '@mui/icons-material/Search';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import PlaceOutlinedIcon from '@mui/icons-material/PlaceOutlined';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { fetchUserOrders } from '../../services/order_service';

const steps = ['Pending', 'Processing', 'Shipped', 'Delivered'];

const statusConfig = {
  pending: { label: 'Pending', color: 'default', step: 0 },
  processing: { label: 'Processing', color: 'warning', step: 1 },
  shipped: { label: 'Shipped', color: 'info', step: 2 },
  delivered: { label: 'Delivered', color: 'success', step: 3 },
  cancelled: { label: 'Cancelled', color: 'error', step: 0 },
  refunded: { label: 'Refunded', color: 'secondary', step: 0 },
};

const formatDate = (value) => {
  if (!value) {
    return 'Not available';
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(value));
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0));
};

const formatAddress = (address) => {
  if (!address || typeof address !== 'object') {
    return 'Address unavailable';
  }

  return [
    address.street,
    address.apt,
    [address.city, address.state].filter(Boolean).join(', '),
    address.zip_code,
  ]
    .filter(Boolean)
    .join(', ');
};

const TrackOrderPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const initialQuery = new URLSearchParams(location.search).get('order') || '';
  const [searchValue, setSearchValue] = useState(initialQuery);

  useEffect(() => {
    if (!isAuthenticated || !user?.id) {
      return;
    }

    const loadOrders = async () => {
      try {
        setLoading(true);
        setError('');
        const response = await fetchUserOrders(user.id, { limit: 50, offset: 0 });
        setOrders(response.orders || []);
      } catch (loadError) {
        setError(loadError.message || 'Unable to load your orders right now.');
      } finally {
        setLoading(false);
      }
    };

    loadOrders();
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    setSearchValue(initialQuery);
  }, [initialQuery]);

  const filteredOrders = useMemo(() => {
    const normalizedSearch = searchValue.trim().toLowerCase();

    if (!normalizedSearch) {
      return orders;
    }

    return orders.filter((order) => {
      return [
        order.order_number,
        order.customer_email,
        order.tracking_number,
      ]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(normalizedSearch));
    });
  }, [orders, searchValue]);

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 5 }, borderRadius: 4, textAlign: 'center' }}>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Track your order
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Order tracking is tied to signed-in customer accounts right now. Log in to view your recent purchases and fulfillment updates.
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
            <Button variant="contained" startIcon={<LoginIcon />} onClick={() => navigate('/login')}>
              Sign in
            </Button>
            <Button variant="outlined" onClick={() => navigate('/contact')}>
              Contact the store
            </Button>
          </Stack>
        </Paper>
      </Container>
    );
  }

  return (
    <Box sx={{ py: { xs: 4, md: 6 }, backgroundColor: (theme) => theme.palette.grey[50], minHeight: '100%' }}>
      <Container maxWidth="lg">
        <Stack spacing={4}>
          <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 4 }}>
            <Grid container spacing={3} alignItems="center">
              <Grid size={{ xs: 12, md: 7 }}>
                <Typography variant="h4" fontWeight={700} gutterBottom>
                  Order tracking
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Search by order number, email address, or tracking number to narrow your recent orders.
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, md: 5 }}>
                <TextField
                  fullWidth
                  value={searchValue}
                  onChange={(event) => setSearchValue(event.target.value)}
                  placeholder="Search orders"
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />,
                  }}
                />
              </Grid>
            </Grid>
          </Paper>

          {error && <Alert severity="error">{error}</Alert>}

          {loading ? (
            <Box sx={{ py: 8, textAlign: 'center' }}>
              <CircularProgress />
            </Box>
          ) : filteredOrders.length === 0 ? (
            <Alert severity="info">
              No matching orders were found. Try a different search term or place your first order from the shop.
            </Alert>
          ) : (
            <Stack spacing={3}>
              {filteredOrders.map((order) => {
                const statusMeta = statusConfig[order.status] || statusConfig.pending;

                return (
                  <Card key={order.id} elevation={2} sx={{ borderRadius: 3 }}>
                    <CardContent sx={{ p: { xs: 3, md: 4 } }}>
                      <Stack spacing={3}>
                        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} justifyContent="space-between">
                          <Box>
                            <Typography variant="h6" fontWeight={700}>
                              {order.order_number}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Placed {formatDate(order.created_at)}
                            </Typography>
                          </Box>
                          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems={{ xs: 'flex-start', sm: 'center' }}>
                            <Chip label={statusMeta.label} color={statusMeta.color} />
                            <Typography variant="subtitle1" fontWeight={700}>
                              {formatCurrency(order.total_amount)}
                            </Typography>
                          </Stack>
                        </Stack>

                        <Stepper activeStep={statusMeta.step} alternativeLabel>
                          {steps.map((stepLabel) => (
                            <Step key={stepLabel}>
                              <StepLabel>{stepLabel}</StepLabel>
                            </Step>
                          ))}
                        </Stepper>

                        <Grid container spacing={3}>
                          <Grid size={{ xs: 12, md: 4 }}>
                            <Stack direction="row" spacing={1.5} alignItems="flex-start">
                              <Inventory2OutlinedIcon color="primary" sx={{ mt: 0.25 }} />
                              <Box>
                                <Typography variant="subtitle2" fontWeight={700}>
                                  Items
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {order.items?.length || 0} items in this order
                                </Typography>
                                {order.items?.slice(0, 3).map((item) => (
                                  <Typography key={item.id} variant="body2">
                                    {item.quantity}x {item.product_name}
                                  </Typography>
                                ))}
                              </Box>
                            </Stack>
                          </Grid>

                          <Grid size={{ xs: 12, md: 4 }}>
                            <Stack direction="row" spacing={1.5} alignItems="flex-start">
                              <LocalShippingOutlinedIcon color="info" sx={{ mt: 0.25 }} />
                              <Box>
                                <Typography variant="subtitle2" fontWeight={700}>
                                  Shipping
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Carrier: {order.carrier_name || 'Assigned after fulfillment'}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Tracking: {order.tracking_number || 'Tracking number pending'}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  Estimated delivery: {formatDate(order.estimated_delivery)}
                                </Typography>
                              </Box>
                            </Stack>
                          </Grid>

                          <Grid size={{ xs: 12, md: 4 }}>
                            <Stack direction="row" spacing={1.5} alignItems="flex-start">
                              <PlaceOutlinedIcon color="secondary" sx={{ mt: 0.25 }} />
                              <Box>
                                <Typography variant="subtitle2" fontWeight={700}>
                                  Destination
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {formatAddress(order.shipping_address)}
                                </Typography>
                              </Box>
                            </Stack>
                          </Grid>
                        </Grid>
                      </Stack>
                    </CardContent>
                  </Card>
                );
              })}
            </Stack>
          )}
        </Stack>
      </Container>
    </Box>
  );
};

export default TrackOrderPage;
