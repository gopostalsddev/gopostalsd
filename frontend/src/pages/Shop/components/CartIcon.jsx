import React, { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Drawer,
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton as ListIconButton,
  Divider,
  Paper,
  Alert
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Delete as DeleteIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import {
  getOrCreateCart,
  getCartTotals,
  removeCartItem,
  updateCartItemQuantity
} from '../../../services/product_service';

const CartIcon = () => {
  const [cart, setCart] = useState(null);
  const [cartOpen, setCartOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load cart on component mount
  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const sessionId = `session_${Date.now()}`; // In a real app, this would come from session management
      const cartData = await getOrCreateCart(sessionId, null, 6);
      if (cartData) {
        setCart(cartData);
      }
    } catch (error) {
      console.error('Error loading cart:', error);
    }
  };

  const handleRemoveItem = async (itemId) => {
    setLoading(true);
    try {
      const result = await removeCartItem(itemId);
      if (result) {
        await loadCart(); // Reload cart to get updated data
        setError(null);
      } else {
        setError('Failed to remove item from cart');
      }
    } catch (error) {
      console.error('Error removing item:', error);
      setError('Failed to remove item from cart');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    
    setLoading(true);
    try {
      const result = await updateCartItemQuantity(itemId, newQuantity);
      if (result) {
        await loadCart(); // Reload cart to get updated data
        setError(null);
      } else {
        setError('Failed to update item quantity');
      }
    } catch (error) {
      console.error('Error updating quantity:', error);
      setError('Failed to update item quantity');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const getItemCount = () => {
    return cart?.items?.reduce((total, item) => total + item.quantity, 0) || 0;
  };

  const getTotalPrice = () => {
    return cart?.totals?.total || 0;
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={() => setCartOpen(true)}
        sx={{ position: 'relative' }}
      >
        <Badge badgeContent={getItemCount()} color="error">
          <ShoppingCartIcon />
        </Badge>
      </IconButton>

      <Drawer
        anchor="right"
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: 400,
            maxWidth: '90vw',
          },
        }}
      >
        <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Shopping Cart</Typography>
            <IconButton onClick={() => setCartOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Cart Items */}
          <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
            {cart?.items?.length > 0 ? (
              <List>
                {cart.items.map((item) => (
                  <React.Fragment key={item.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemText
                        primary={item.product_name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              SKU: {item.product_sku}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {formatPrice(item.unit_price)} each
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                              <Button
                                size="small"
                                variant="outlined"
                                onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                                disabled={loading || item.quantity <= 1}
                              >
                                -
                              </Button>
                              <Typography variant="body2" sx={{ minWidth: 20, textAlign: 'center' }}>
                                {item.quantity}
                              </Typography>
                              <Button
                                size="small"
                                variant="outlined"
                                onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                disabled={loading}
                              >
                                +
                              </Button>
                            </Box>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <Box sx={{ textAlign: 'right' }}>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {formatPrice(item.total_price)}
                          </Typography>
                          <ListIconButton
                            edge="end"
                            onClick={() => handleRemoveItem(item.id)}
                            disabled={loading}
                            color="error"
                          >
                            <DeleteIcon />
                          </ListIconButton>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <ShoppingCartIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Your cart is empty
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Add some products to get started
                </Typography>
              </Box>
            )}
          </Box>

          {/* Cart Summary */}
          {cart?.items?.length > 0 && (
            <Paper sx={{ p: 2, mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Subtotal:</Typography>
                <Typography>{formatPrice(cart.totals?.subtotal || 0)}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography>Tax:</Typography>
                <Typography>{formatPrice(cart.totals?.tax || 0)}</Typography>
              </Box>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">Total:</Typography>
                <Typography variant="h6" fontWeight="bold" color="primary">
                  {formatPrice(cart.totals?.total || 0)}
                </Typography>
              </Box>
              <Button
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ textTransform: 'none' }}
              >
                Proceed to Checkout
              </Button>
            </Paper>
          )}
        </Box>
      </Drawer>
    </>
  );
};

export default CartIcon;
