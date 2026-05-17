import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Divider,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Chip,
  Stack
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Delete as DeleteIcon,
  ShoppingCart as ShoppingCartIcon,
  LocalShipping as ShippingIcon,
  Login as LoginIcon
} from '@mui/icons-material';
import { useCartOperations, useCartFormatting } from '../hooks/useCart';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { CartTotals } from './CartTotals';
import { ShippingOptions } from './ShippingOptions';

export function Cart() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const {
    cart,
    loading,
    error,
    updateItemQuantity,
    removeItemFromCart,
    clearEntireCart,
    getCartStats
  } = useCartOperations();

  const { formatPrice, getCartSummaryText } = useCartFormatting();

  const cartStats = getCartStats();

  const handleQuantityChange = async (cartItemId, newQuantity) => {
    const result = await updateItemQuantity(cartItemId, newQuantity);
    if (!result.success) {
      console.error('Failed to update quantity:', result.error);
    }
  };

  const handleRemoveItem = async (cartItemId) => {
    const result = await removeItemFromCart(cartItemId);
    if (!result.success) {
      console.error('Failed to remove item:', result.error);
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      const result = await clearEntireCart();
      if (!result.success) {
        console.error('Failed to clear cart:', result.error);
      }
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading cart...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper elevation={2} sx={{ p: 6, textAlign: 'center' }}>
          <LoginIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Login Required
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Please log in to view and manage your shopping cart.
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<LoginIcon />}
            onClick={() => navigate('/login')}
            sx={{ px: 4 }}
          >
            Log In
          </Button>
        </Paper>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (cartStats.isEmpty) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper elevation={2} sx={{ p: 6, textAlign: 'center' }}>
          <ShoppingCartIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Your Cart is Empty
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Looks like you haven't added any items to your cart yet.
          </Typography>
          <Button
            variant="contained"
            size="large"
            href="/shop"
            sx={{ px: 4 }}
            
          >
            Browse Products
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Cart Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Shopping Cart
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {getCartSummaryText()}
        </Typography>
      </Box>

      <Box display="flex" flexDirection={{ xs: 'column', lg: 'row' }} gap={4}>
        {/* Cart Items */}
        <Box flex={2}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
              <Typography variant="h6">
                Cart Items ({cartStats.itemCount})
              </Typography>
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<DeleteIcon />}
                onClick={handleClearCart}
              >
                Clear Cart
              </Button>
            </Box>

            <Divider sx={{ mb: 3 }} />

            <Stack spacing={3}>
              {cart.items.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  onQuantityChange={(quantity) => handleQuantityChange(item.id, quantity)}
                  onRemove={() => handleRemoveItem(item.id)}
                />
              ))}
            </Stack>
          </Paper>
        </Box>

        {/* Cart Summary */}
        <Box flex={1}>
          <Box position="sticky" top={24}>
            <CartTotals cart={cart} />
            
            <Box sx={{ mt: 3 }}>
              <ShippingOptions />
            </Box>

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                size="large"
                fullWidth
                href="/checkout"
                sx={{ py: 1.5 }}
              >
                Proceed to Checkout
              </Button>
            </Box>

            <Box sx={{ mt: 2 }}>
              <Button
                variant="outlined"
                size="large"
                fullWidth
                href="/products"
              >
                Continue Shopping
              </Button>
            </Box>
          </Box>
        </Box>
      </Box>
    </Container>
  );
}

// Cart Item Component
function CartItem({ item, onQuantityChange, onRemove }) {
  const { formatPrice, formatItemOptions } = useCartFormatting();

  return (
    <Card variant="outlined">
      <CardContent>
        <Box display="flex" gap={2}>
          {/* Product Image Placeholder */}
          <Box
            sx={{
              width: 80,
              height: 80,
              bgcolor: 'grey.100',
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <Typography variant="caption" color="text.secondary">
              Image
            </Typography>
          </Box>

          {/* Product Details */}
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              {item.product_name}
            </Typography>
            
            {item.product_sku && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                SKU: {item.product_sku}
              </Typography>
            )}

            {item.selected_options && Object.keys(item.selected_options).length > 0 && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Options: {formatItemOptions(item.selected_options)}
                </Typography>
              </Box>
            )}

            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" color="primary">
                {formatPrice(item.total_price)}
              </Typography>
              
              <Box display="flex" alignItems="center" gap={1}>
                <IconButton
                  size="small"
                  onClick={() => onQuantityChange(item.quantity - 1)}
                  disabled={item.quantity <= 1}
                >
                  <RemoveIcon />
                </IconButton>
                
                <Typography variant="body1" sx={{ minWidth: 40, textAlign: 'center' }}>
                  {item.quantity}
                </Typography>
                
                <IconButton
                  size="small"
                  onClick={() => onQuantityChange(item.quantity + 1)}
                >
                  <AddIcon />
                </IconButton>
              </Box>
            </Box>
          </Box>

          {/* Remove Button */}
          <Box>
            <IconButton
              color="error"
              onClick={onRemove}
              sx={{ alignSelf: 'flex-start' }}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
