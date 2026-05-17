import React from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Stack,
  Chip,
} from "@mui/material";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import LocalMallOutlinedIcon from "@mui/icons-material/LocalMallOutlined";
import SettingsApplicationsOutlinedIcon from "@mui/icons-material/SettingsApplicationsOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
import { useNavigate } from "react-router-dom";

const AdminPage = () => {
  const navigate = useNavigate();

  const managementTiles = [
    {
      title: "Product Management",
      description:
        "Curate the product catalog, manage categories, and ensure every listing is classification-ready before it reaches the storefront.",
      icon: <Inventory2OutlinedIcon sx={{ fontSize: 40 }} color="primary" />,
      actionLabel: "Manage Products",
      onClick: () => navigate("/admin/products"),
      highlights: ["Category curation", "Pricing alignment", "Vendor sync"],
    },
    {
      title: "Order Management",
      description:
        "Monitor new orders, oversee fulfillment, and maintain best-in-class communication with your customers throughout the delivery cycle.",
      icon: <LocalMallOutlinedIcon sx={{ fontSize: 40 }} color="secondary" />,
      actionLabel: "Go to Orders",
      onClick: () => navigate("/admin/orders"),
      highlights: ["Fulfillment insights", "Customer updates", "Exception tracking"],
    },
  ];

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
        <Box sx={{ textAlign: "center", mb: 6 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          Welcome to the Go Postal SD Admin Console
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 720, mx: "auto" }}>
          Select a management workspace to get started. Each module is optimized for deep operational work with the
          tools and insights your team relies on every day.
          </Typography>
        </Box>

        <Grid
          container
          spacing={4}
          sx={{ mb: 4, justifyContent: "center" }}
        >
          {managementTiles.map((tile) => (
            <Grid
              key={tile.title}
              item
              xs={12}
              md={6}
              sx={{ display: "flex", justifyContent: "center" }}
            >
              <Card
                elevation={5}
                sx={{
                  width: "100%",
                  maxWidth: 520,
                  height: "100%",
                  borderRadius: 4,
                  display: "flex",
                  flexDirection: "column",
                  p: 2,
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Stack spacing={2}>
                    <Box>{tile.icon}</Box>
                    <Typography variant="h5" fontWeight={700}>
                      {tile.title}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      {tile.description}
                    </Typography>
                    <Stack direction="row" spacing={1} mt={1} flexWrap="wrap" useFlexGap>
                      {tile.highlights.map((label) => (
                        <Chip key={label} label={label} color="primary" variant="outlined" sx={{ textTransform: "capitalize" }} />
                      ))}
                    </Stack>
                  </Stack>
                </CardContent>
                <CardActions sx={{ justifyContent: "flex-end", px: 2, pb: 2 }}>
                  <Button variant="contained" size="large" onClick={tile.onClick}>
                    {tile.actionLabel}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default AdminPage;