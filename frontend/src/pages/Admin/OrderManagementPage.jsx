import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Typography,
  Grid,
  Paper,
  Stack,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Divider,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  TextField,
} from "@mui/material";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import InsightsIcon from "@mui/icons-material/Insights";
import SyncIcon from '@mui/icons-material/Sync';
import NorthEastIcon from '@mui/icons-material/NorthEast';
import { fetchAllOrders, fetchOrderStatuses, updateOrderStatus } from '../../services/order_service';

const statusConfig = {
  processing: { label: "Processing", color: "warning" },
  pending: { label: "Pending", color: "default" },
  shipped: { label: "Shipped", color: "info" },
  delivered: { label: "Delivered", color: "success" },
  cancelled: { label: "Cancelled", color: "error" },
  refunded: { label: 'Refunded', color: 'secondary' },
};

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(Number(value || 0));
};

const formatDateTime = (value) => {
  if (!value) {
    return 'Not available';
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value));
};

const OrderManagementPage = () => {
  const [orders, setOrders] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [statusDraft, setStatusDraft] = useState('pending');
  const [trackingNumberDraft, setTrackingNumberDraft] = useState('');
  const [carrierNameDraft, setCarrierNameDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadOrders = async (statusFilter = selectedStatus) => {
    try {
      setLoading(true);
      setError('');
      const params = { limit: 50, offset: 0 };
      if (statusFilter && statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await fetchAllOrders(params);
      setOrders(response.orders || []);
    } catch (loadError) {
      setError(loadError.message || 'Unable to load orders.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError('');
        const [ordersResponse, statusesResponse] = await Promise.all([
          fetchAllOrders({ limit: 50, offset: 0 }),
          fetchOrderStatuses(),
        ]);
        setOrders(ordersResponse.orders || []);
        setStatuses(statusesResponse || []);
      } catch (loadError) {
        setError(loadError.message || 'Unable to load order management data.');
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const summary = useMemo(() => {
    const thisWeekCutoff = new Date();
    thisWeekCutoff.setDate(thisWeekCutoff.getDate() - 7);

    const ordersThisWeek = orders.filter((order) => new Date(order.created_at) >= thisWeekCutoff).length;
    const ordersInFulfillment = orders.filter((order) => ['pending', 'processing', 'shipped'].includes(order.status)).length;
    const completedToday = orders.filter((order) => {
      if (order.status !== 'delivered') {
        return false;
      }

      const deliveredDate = order.delivered_at ? new Date(order.delivered_at) : null;
      if (!deliveredDate) {
        return false;
      }

      const today = new Date();
      return deliveredDate.toDateString() === today.toDateString();
    }).length;

    const averageOrderValue = orders.length
      ? orders.reduce((total, order) => total + Number(order.total_amount || 0), 0) / orders.length
      : 0;

    return [
      {
        title: 'Orders This Week',
        value: ordersThisWeek,
        icon: <PendingActionsIcon fontSize="large" color="primary" />,
        caption: `${orders.length} total orders in current view`,
      },
      {
        title: 'Orders In Fulfillment',
        value: ordersInFulfillment,
        icon: <LocalShippingIcon fontSize="large" color="info" />,
        caption: 'Pending, processing, or shipped',
      },
      {
        title: 'Completed Today',
        value: completedToday,
        icon: <AssignmentTurnedInIcon fontSize="large" color="success" />,
        caption: 'Delivered orders marked today',
      },
      {
        title: 'Average Order Value',
        value: formatCurrency(averageOrderValue),
        icon: <InsightsIcon fontSize="large" color="secondary" />,
        caption: 'Across the filtered order set',
      },
    ];
  }, [orders]);

  const openOrderDialog = (order) => {
    setSelectedOrder(order);
    setStatusDraft(order.status || 'pending');
    setTrackingNumberDraft(order.tracking_number || '');
    setCarrierNameDraft(order.carrier_name || '');
    setSuccess('');
  };

  const closeOrderDialog = () => {
    setSelectedOrder(null);
    setStatusDraft('pending');
    setTrackingNumberDraft('');
    setCarrierNameDraft('');
  };

  const handleFilterChange = async (event) => {
    const nextStatus = event.target.value;
    setSelectedStatus(nextStatus);
    await loadOrders(nextStatus);
  };

  const handleStatusUpdate = async () => {
    if (!selectedOrder) {
      return;
    }

    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const updatedOrder = await updateOrderStatus(selectedOrder.id, {
        status: statusDraft,
        tracking_number: trackingNumberDraft || undefined,
        carrier_name: carrierNameDraft || undefined,
      });

      setOrders((currentOrders) => currentOrders.map((order) => (
        order.id === updatedOrder.id ? updatedOrder : order
      )));
      setSelectedOrder(updatedOrder);
      setSuccess(`Order ${updatedOrder.order_number} updated successfully.`);
    } catch (saveError) {
      setError(saveError.message || 'Unable to update order status.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box
      sx={{
        flex: 1,
        py: { xs: 4, md: 7 },
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(circle at top left, rgba(7,59,102,0.1), transparent 26%), radial-gradient(circle at bottom right, rgba(182,73,38,0.08), transparent 26%)',
          pointerEvents: 'none',
        }}
      />
      <Box
        sx={{
          maxWidth: "1300px",
          mx: "auto",
          px: { xs: 3, md: 6 },
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: { xs: "flex-start", md: "center" },
            justifyContent: "space-between",
            flexDirection: { xs: "column", md: "row" },
            gap: 3,
            mb: 4,
          }}
        >
            <Paper
              elevation={0}
              sx={{
                p: { xs: 3, md: 4 },
                borderRadius: 6,
                flex: 1,
                border: '1px solid rgba(24,33,42,0.08)',
                background: 'linear-gradient(135deg, rgba(10,19,31,0.98), rgba(7,59,102,0.92) 58%, rgba(182,73,38,0.82) 130%)',
                color: 'white',
              }}
            >
              <Chip label="Admin console" sx={{ mb: 2, backgroundColor: 'rgba(255,255,255,0.14)', color: 'white' }} />
              <Typography variant="h3" sx={{ fontSize: { xs: '2rem', md: '3rem' } }} fontWeight={700} gutterBottom>
              Order Management
            </Typography>
              <Typography variant="body1" sx={{ maxWidth: 700, opacity: 0.9, lineHeight: 1.8 }}>
              Track fulfillment progress, identify orders that need attention, and keep your customers informed at every milestone.
            </Typography>
            </Paper>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} flexShrink={0} alignSelf={{ xs: 'stretch', md: 'flex-end' }}>
            <Button variant="contained" color="primary" startIcon={<SyncIcon />} onClick={() => loadOrders()}>
              Refresh Orders
            </Button>
            <TextField
              select
              size="small"
              value={selectedStatus}
              onChange={handleFilterChange}
              sx={{ minWidth: 180, backgroundColor: 'white', borderRadius: 1 }}
            >
              <MenuItem value="all">All statuses</MenuItem>
              {statuses.map((status) => (
                <MenuItem key={status} value={status}>
                  {statusConfig[status]?.label || status}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}

        <Grid container spacing={3} sx={{ mb: 4 }}>
          {summary.map((card) => (
            <Grid key={card.title} size={{ xs: 12, sm: 6, md: 3 }}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 5,
                  height: "100%",
                  border: '1px solid rgba(24,33,42,0.08)',
                  background: 'linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,255,255,0.78))',
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <Stack direction="row" alignItems="center" spacing={2}>
                  {card.icon}
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      {card.title}
                    </Typography>
                    <Typography variant="h5" fontWeight={700} sx={{ mt: 0.5 }}>
                      {card.value}
                    </Typography>
                    <Typography variant="caption" color="success.main">
                      {card.caption}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, borderRadius: 5, border: '1px solid rgba(24,33,42,0.08)', backgroundColor: 'background.paper' }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: { xs: "flex-start", sm: "center" },
              flexDirection: { xs: "column", sm: "row" },
              gap: 2,
              mb: 2,
            }}
          >
            <div>
              <Typography variant="h5" fontWeight={700}>
                Recent Orders
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Live order activity with fulfillment status, customer details, and administrative controls.
              </Typography>
            </div>
            <Chip label={`Showing ${orders.length} orders`} variant="outlined" />
          </Box>

          <Divider sx={{ mb: 2 }} />

          {loading ? (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <CircularProgress />
            </Box>
          ) : orders.length === 0 ? (
            <Alert severity="info">No orders match the current filter.</Alert>
          ) : (
            <TableContainer>
              <Table size="medium">
                <TableHead>
                  <TableRow>
                    <TableCell>Order #</TableCell>
                    <TableCell>Customer</TableCell>
                    <TableCell>Placed</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.map((order) => {
                    const statusMeta = statusConfig[order.status] || statusConfig.pending;
                    return (
                      <TableRow key={order.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {order.order_number}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {order.items?.length || 0} items
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {order.customer_first_name} {order.customer_last_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {order.customer_email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {formatDateTime(order.created_at)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" fontWeight={600}>
                            {formatCurrency(order.total_amount)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={statusMeta.label}
                            color={statusMeta.color}
                            size="small"
                            sx={{ fontWeight: 600, textTransform: "capitalize" }}
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={1} justifyContent="flex-end">
                            <Button variant="outlined" size="small" endIcon={<NorthEastIcon />} onClick={() => openOrderDialog(order)}>
                              Details
                            </Button>
                            <Button variant="contained" size="small" color="primary" onClick={() => openOrderDialog(order)}>
                              Update Status
                            </Button>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      </Box>

      <Dialog open={Boolean(selectedOrder)} onClose={closeOrderDialog} fullWidth maxWidth="md">
        <DialogTitle>Order Details</DialogTitle>
        <DialogContent dividers>
          {selectedOrder && (
            <Stack spacing={3} sx={{ pt: 1 }}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Order Number</Typography>
                  <Typography variant="body1" fontWeight={700}>{selectedOrder.order_number}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Customer</Typography>
                  <Typography variant="body1" fontWeight={700}>
                    {selectedOrder.customer_first_name} {selectedOrder.customer_last_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">{selectedOrder.customer_email}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Placed</Typography>
                  <Typography variant="body2">{formatDateTime(selectedOrder.created_at)}</Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="text.secondary">Total</Typography>
                  <Typography variant="body2">{formatCurrency(selectedOrder.total_amount)}</Typography>
                </Grid>
              </Grid>

              <Divider />

              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    select
                    label="Status"
                    value={statusDraft}
                    onChange={(event) => setStatusDraft(event.target.value)}
                  >
                    {statuses.map((status) => (
                      <MenuItem key={status} value={status}>
                        {statusConfig[status]?.label || status}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    label="Tracking Number"
                    value={trackingNumberDraft}
                    onChange={(event) => setTrackingNumberDraft(event.target.value)}
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <TextField
                    fullWidth
                    label="Carrier Name"
                    value={carrierNameDraft}
                    onChange={(event) => setCarrierNameDraft(event.target.value)}
                  />
                </Grid>
              </Grid>

              <Box>
                <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                  Items
                </Typography>
                <Stack spacing={1.5}>
                  {selectedOrder.items?.map((item) => (
                    <Paper key={item.id} variant="outlined" sx={{ p: 2, borderRadius: 2 }}>
                      <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={1}>
                        <Box>
                          <Typography variant="body1" fontWeight={600}>{item.product_name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            SKU: {item.product_sku || 'N/A'}
                          </Typography>
                        </Box>
                        <Typography variant="body2">
                          {item.quantity} x {formatCurrency(item.unit_price)} = {formatCurrency(item.total_price)}
                        </Typography>
                      </Stack>
                    </Paper>
                  ))}
                </Stack>
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeOrderDialog}>Close</Button>
          <Button variant="contained" onClick={handleStatusUpdate} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OrderManagementPage;

