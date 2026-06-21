import React, { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import AttachMoneyOutlinedIcon from '@mui/icons-material/AttachMoneyOutlined';
import NorthEastIcon from '@mui/icons-material/NorthEast';
import VerifiedUserOutlinedIcon from '@mui/icons-material/VerifiedUserOutlined';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { fetchUserOrders } from '../../services/order_service';

const statusConfig = {
  pending: { label: 'Pending', color: 'default' },
  processing: { label: 'Processing', color: 'warning' },
  shipped: { label: 'Shipped', color: 'info' },
  delivered: { label: 'Delivered', color: 'success' },
  cancelled: { label: 'Cancelled', color: 'error' },
  refunded: { label: 'Refunded', color: 'secondary' },
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
    return 'No address on file';
  }

  return [
    address.street,
    address.apt,
    [address.city, address.state].filter(Boolean).join(', '),
    address.zip_code,
    address.country,
  ]
    .filter(Boolean)
    .join(', ');
};

const AccountPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadOrders = async () => {
      if (!user?.id) {
        setLoadingOrders(false);
        return;
      }

      try {
        setLoadingOrders(true);
        setError('');
        const response = await fetchUserOrders(user.id, { limit: 10, offset: 0 });
        setOrders(response.orders || []);
      } catch (loadError) {
        setError(loadError.message || 'Unable to load your orders right now.');
      } finally {
        setLoadingOrders(false);
      }
    };

    loadOrders();
  }, [user?.id]);

  const inProgressOrders = orders.filter((order) => ['pending', 'processing', 'shipped'].includes(order.status)).length;
  const lifetimeSpend = orders.reduce((total, order) => total + Number(order.total_amount || 0), 0);
  const mostRecentOrder = orders[0];

  const summaryCards = [
    {
      title: 'Orders placed',
      value: orders.length,
      caption: mostRecentOrder ? `Latest: ${mostRecentOrder.order_number}` : 'No orders yet',
      icon: <Inventory2OutlinedIcon color="primary" fontSize="large" />,
    },
    {
      title: 'Active orders',
      value: inProgressOrders,
      caption: 'Pending, processing, or shipped',
      icon: <LocalShippingOutlinedIcon color="info" fontSize="large" />,
    },
    {
      title: 'Lifetime spend',
      value: formatCurrency(lifetimeSpend),
      caption: 'Across completed checkouts',
      icon: <AttachMoneyOutlinedIcon color="success" fontSize="large" />,
    },
  ];

  return (
    <Box sx={{ py: { xs: 4, md: 7 }, minHeight: '100%', position: 'relative', overflow: 'hidden' }}>
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(circle at top right, rgba(182,73,38,0.08), transparent 24%), radial-gradient(circle at bottom left, rgba(7,59,102,0.1), transparent 28%)',
          pointerEvents: 'none',
        }}
      />
      <Container maxWidth="lg">
        <Stack spacing={4}>
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3, md: 5 },
              borderRadius: 6,
              border: '1px solid rgba(24,33,42,0.08)',
              background: 'linear-gradient(135deg, rgba(10,19,31,0.98), rgba(7,59,102,0.92) 58%, rgba(182,73,38,0.82) 130%)',
              color: 'white',
            }}
          >
            <Grid container spacing={4} alignItems="end">
              <Grid size={{ xs: 12, md: 8 }}>
                <Chip label="Customer account" sx={{ mb: 2, backgroundColor: 'rgba(255,255,255,0.14)', color: 'white' }} />
                <Typography variant="h2" sx={{ fontSize: { xs: '2.2rem', md: '3.4rem' }, mb: 1.5 }}>
                  Welcome back, {user?.first_name || 'Customer'}
                </Typography>
                <Typography variant="body1" sx={{ maxWidth: 640, opacity: 0.9, lineHeight: 1.8 }}>
                  Review your profile, keep an eye on in-flight orders, and move back into production-ready ordering without losing track of the details that matter.
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    borderRadius: 4,
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    color: 'white',
                    border: '1px solid rgba(255,255,255,0.14)',
                  }}
                >
                  <Typography variant="overline" sx={{ opacity: 0.7 }}>
                    Member snapshot
                  </Typography>
                  <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
                    {mostRecentOrder ? `Latest order ${mostRecentOrder.order_number}` : 'Your workspace is ready'}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.85, mb: 3, lineHeight: 1.7 }}>
                    Use your account as the operational home for reorder history, shipment follow-up, and customer support context.
                  </Typography>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                    <Button variant="contained" color="secondary" onClick={() => navigate('/track-order')}>
                      Track orders
                    </Button>
                    <Button variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.65)' }} onClick={() => navigate('/shop')} endIcon={<NorthEastIcon />}>
                      Shop again
                    </Button>
                  </Stack>
                </Paper>
              </Grid>
            </Grid>
          </Paper>

          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 4 }}>
              <Paper elevation={0} sx={{ p: 3.5, borderRadius: 5, height: '100%', border: '1px solid rgba(24,33,42,0.08)', background: 'linear-gradient(180deg, rgba(255,255,255,0.9), rgba(244,239,231,0.85))' }}>
                <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2.5 }}>
                  <PersonOutlineIcon color="primary" />
                  <Typography variant="h5" fontWeight={700}>
                    Profile
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} sx={{ mb: 2.5 }}>
                  <Chip icon={<VerifiedUserOutlinedIcon />} label={user?.email_verified ? 'Verified account' : 'Verification pending'} color={user?.email_verified ? 'success' : 'warning'} />
                  <Chip label={user?.role || 'Customer'} variant="outlined" />
                </Stack>
                <Stack spacing={1.5}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Full name
                    </Typography>
                    <Typography variant="body1" fontWeight={600}>
                      {[user?.first_name, user?.last_name].filter(Boolean).join(' ') || 'Not provided'}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Email
                    </Typography>
                    <Typography variant="body1">{user?.email || 'Not provided'}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Account type
                    </Typography>
                    <Typography variant="body1">{user?.role || 'Customer'}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Shipping address
                    </Typography>
                    <Typography variant="body2">{formatAddress(user?.shipping_address)}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Billing address
                    </Typography>
                    <Typography variant="body2">{formatAddress(user?.billing_address)}</Typography>
                  </Box>
                </Stack>
              </Paper>
            </Grid>

            <Grid size={{ xs: 12, md: 8 }}>
              <Grid container spacing={3}>
                {summaryCards.map((card) => (
                  <Grid size={{ xs: 12, sm: 4 }} key={card.title}>
                    <Paper elevation={0} sx={{ p: 3, borderRadius: 5, height: '100%', border: '1px solid rgba(24,33,42,0.08)', background: 'linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.76))' }}>
                      <Stack spacing={1.5}>
                        {card.icon}
                        <Typography variant="overline" color="text.secondary">
                          {card.title}
                        </Typography>
                        <Typography variant="h5" fontWeight={700}>
                          {card.value}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {card.caption}
                        </Typography>
                      </Stack>
                    </Paper>
                  </Grid>
                ))}

                <Grid size={{ xs: 12 }}>
                  <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, borderRadius: 5, border: '1px solid rgba(24,33,42,0.08)', backgroundColor: 'background.paper' }}>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} sx={{ mb: 2 }}>
                      <Box>
                        <Typography variant="h5" fontWeight={700}>
                          Recent orders
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Your latest purchases and fulfillment status.
                        </Typography>
                      </Box>
                      <Button variant="text" onClick={() => navigate('/track-order')}>
                        View all orders
                      </Button>
                    </Stack>

                    <Divider sx={{ mb: 2 }} />

                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                    {loadingOrders ? (
                      <Box sx={{ py: 5, textAlign: 'center' }}>
                        <CircularProgress />
                      </Box>
                    ) : orders.length === 0 ? (
                      <Alert severity="info">
                        No orders are attached to this account yet. Once you check out, they will appear here.
                      </Alert>
                    ) : (
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Order</TableCell>
                              <TableCell>Date</TableCell>
                              <TableCell>Status</TableCell>
                              <TableCell align="right">Total</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {orders.map((order) => {
                              const statusMeta = statusConfig[order.status] || statusConfig.pending;

                              return (
                                <TableRow
                                  key={order.id}
                                  hover
                                  sx={{ cursor: 'pointer' }}
                                  onClick={() => navigate(`/track-order?order=${encodeURIComponent(order.order_number)}`)}
                                >
                                  <TableCell>
                                    <Typography variant="body2" fontWeight={700}>
                                      {order.order_number}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      {order.items?.length || 0} items
                                    </Typography>
                                  </TableCell>
                                  <TableCell>{formatDate(order.created_at)}</TableCell>
                                  <TableCell>
                                    <Chip label={statusMeta.label} color={statusMeta.color} size="small" />
                                  </TableCell>
                                  <TableCell align="right">{formatCurrency(order.total_amount)}</TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Stack>
      </Container>
    </Box>
  );
};

export default AccountPage;
