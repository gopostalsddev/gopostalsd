import React, { useMemo } from "react";
import {
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
} from "@mui/material";
import LocalShippingIcon from "@mui/icons-material/LocalShipping";
import AssignmentTurnedInIcon from "@mui/icons-material/AssignmentTurnedIn";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import InsightsIcon from "@mui/icons-material/Insights";

const statusConfig = {
  processing: { label: "Processing", color: "warning" },
  pending: { label: "Pending", color: "default" },
  shipped: { label: "Shipped", color: "info" },
  delivered: { label: "Delivered", color: "success" },
  cancelled: { label: "Cancelled", color: "error" },
};

const OrderManagementPage = () => {
  // Placeholder analytics – replace with API integration when backend is ready
  const { summary, recentOrders } = useMemo(
    () => ({
      summary: [
        {
          title: "Orders This Week",
          value: 24,
          icon: <PendingActionsIcon fontSize="large" color="primary" />,
          caption: "+18% vs last week",
        },
        {
          title: "Orders In Fulfillment",
          value: 9,
          icon: <LocalShippingIcon fontSize="large" color="info" />,
          caption: "5 awaiting carrier pickup",
        },
        {
          title: "Completed Today",
          value: 7,
          icon: <AssignmentTurnedInIcon fontSize="large" color="success" />,
          caption: "All shipments confirmed",
        },
        {
          title: "Average Order Value",
          value: "$128.40",
          icon: <InsightsIcon fontSize="large" color="secondary" />,
          caption: "+$14.20 vs 30-day avg",
        },
      ],
      recentOrders: [
        {
          orderNumber: "GP20241107ABCD",
          customer: "Maria Gomez",
          total: 156.2,
          status: "processing",
          createdAt: "Nov 7, 10:24 AM",
        },
        {
          orderNumber: "GP20241106XC92",
          customer: "Derrick Lang",
          total: 89.99,
          status: "shipped",
          createdAt: "Nov 6, 8:02 PM",
        },
        {
          orderNumber: "GP20241106PZ31",
          customer: "Sarah Johnson",
          total: 245.0,
          status: "delivered",
          createdAt: "Nov 6, 2:37 PM",
        },
        {
          orderNumber: "GP20241105ML10",
          customer: "Alan Chen",
          total: 64.5,
          status: "pending",
          createdAt: "Nov 5, 5:46 PM",
        },
      ],
    }),
    []
  );

  return (
    <Box
      sx={{
        flex: 1,
        backgroundColor: (theme) => theme.palette.grey[50],
        py: { xs: 4, md: 6 },
      }}
    >
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
          <div>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              Order Management
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 560 }}>
              Track fulfillment progress, identify orders that need attention, and keep your customers informed at every milestone.
            </Typography>
          </div>
          <Stack direction="row" spacing={2} flexShrink={0}>
            <Button variant="contained" color="primary">
              Export Orders
            </Button>
            <Button variant="outlined" color="primary">
              Configure Notifications
            </Button>
          </Stack>
        </Box>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          {summary.map((card) => (
            <Grid key={card.title} item xs={12} sm={6} md={3}>
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  borderRadius: 3,
                  height: "100%",
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

        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 3 }}>
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
              <Typography variant="h6" fontWeight={700}>
                Recent Orders
              </Typography>
              <Typography variant="body2" color="text.secondary">
                A quick look at the latest orders requiring review or fulfillment.
              </Typography>
            </div>
            <Button variant="text" color="primary">
              View All Orders
            </Button>
          </Box>

          <Divider sx={{ mb: 2 }} />

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
                {recentOrders.map((order) => {
                  const statusMeta = statusConfig[order.status] || statusConfig.pending;
                  return (
                    <TableRow key={order.orderNumber} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {order.orderNumber}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{order.customer}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {order.createdAt}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight={600}>
                          ${order.total.toFixed(2)}
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
                          <Button variant="outlined" size="small">
                            Details
                          </Button>
                          <Button variant="contained" size="small" color="primary">
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
        </Paper>
      </Box>
    </Box>
  );
};

export default OrderManagementPage;

