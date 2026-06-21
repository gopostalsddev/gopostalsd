import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  Paper
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Favorite as FavoriteIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import {
  fetchProductOptions,
  calculateProductPrice
} from '../../../services/product_service';
import { useCartOperations } from '../../../hooks/useCart';
import { useAuth } from '../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import logoImage from '../../../assets/logo.png';

const ProductCard = ({ product, onAddToCart, onToggleFavorite, isFavorite, onViewProduct }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { addItemToCart } = useCartOperations();
  const [options, setOptions] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState({});
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pricingLoading, setPricingLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState(null);

  // Load product options when component mounts
  useEffect(() => {
    const loadOptions = async () => {
      if (!product.vendor_product_id) return;
      
      setLoading(true);
      try {
        const productOptions = await fetchProductOptions(product.vendor_product_id, 6); // Canada store
        setOptions(productOptions);
      } catch (error) {
        console.error('Error loading product options:', error);
        setError('Failed to load product options');
      } finally {
        setLoading(false);
      }
    };

    loadOptions();
  }, [product.vendor_product_id]);

  // Calculate price when options change
  useEffect(() => {
    const calculatePrice = async () => {
      if (!product.vendor_product_id || Object.keys(selectedOptions).length === 0) {
        setPricing(null);
        return;
      }

      const optionIds = Object.values(selectedOptions).filter(id => id !== '');
      if (optionIds.length === 0) {
        setPricing(null);
        return;
      }

      setPricingLoading(true);
      try {
        const priceData = await calculateProductPrice(product.vendor_product_id, optionIds, 6);
        setPricing(priceData);
        setError(null);
      } catch (error) {
        console.error('Error calculating price:', error);
        setError('Failed to calculate price');
        setPricing(null);
      } finally {
        setPricingLoading(false);
      }
    };

    calculatePrice();
  }, [selectedOptions, product.vendor_product_id]);

  const handleOptionChange = (group, optionId) => {
    setSelectedOptions(prev => ({
      ...prev,
      [group]: optionId
    }));
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please select all required options');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Add item to cart using the new cart system
      const optionIds = Object.values(selectedOptions).filter(id => id !== '');
      const result = await addItemToCart(
        product.vendor_product_id,
        optionIds,
        quantity
      );

      if (result.success) {
        onAddToCart(result.cartItem);
        setDialogOpen(false);
        setError(null);
        // Reset form
        setSelectedOptions({});
        setQuantity(1);
      } else {
        setError(result.error || 'Failed to add item to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      setError('Failed to add item to cart');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProduct = () => {
    if (onViewProduct) {
      onViewProduct(product);
    } else {
      setDialogOpen(true);
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setError(null);
  };

  const getProductImage = () => {
    return product.image || logoImage;
  };

  const formatPrice = (price) => {
    if (!price) return 'Price not available';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const isAddToCartDisabled = () => {
    return !pricing || Object.keys(selectedOptions).length === 0 || pricingLoading;
  };

  return (
    <>
      <Card 
        sx={{ 
          height: '100%',
          width: '100%',
          maxWidth: '350px', // Constrain card width
          display: 'flex',
          flexDirection: 'column',
          boxShadow: 2,
          borderRadius: 3,
          overflow: 'hidden',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 8,
            transform: 'translateY(-4px)',
          }
        }}
      >
        {/* Product Image - Small Square */}
        <Box sx={{ 
          position: 'relative',
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          p: 2,
          backgroundColor: '#f5f5f5'
        }}>
          <img
            src={getProductImage()}
            alt={product.name}
            style={{
              width: '100px',
              height: '100px',
              objectFit: 'cover',
              borderRadius: '8px',
              border: '2px solid #e0e0e0'
            }}
          />
          <IconButton
            sx={{ position: 'absolute', top: 8, right: 8 }}
            onClick={() => onToggleFavorite(product.id)}
            color={isFavorite ? 'error' : 'default'}
          >
            <FavoriteIcon />
          </IconButton>
        </Box>

        <CardContent sx={{ 
          flexGrow: 1, 
          pb: 1,
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          {/* Product Name */}
          <Typography 
            variant="h6" 
            component="h3" 
            gutterBottom
            sx={{
              wordWrap: 'break-word',
              overflowWrap: 'break-word',
              hyphens: 'auto',
              maxWidth: '100%',
              lineHeight: 1.2
            }}
          >
            {product.name}
          </Typography>

          {/* Product SKU */}
          {product.sku && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              gutterBottom
              sx={{
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                hyphens: 'auto',
                maxWidth: '100%'
              }}
            >
              SKU: {product.sku}
            </Typography>
          )}

          {/* Product Description */}
          {product.description && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                mb: 2,
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                hyphens: 'auto',
                maxWidth: '100%',
                lineHeight: 1.5
              }}
            >
              {product.description.length > 100 
                ? `${product.description.substring(0, 100)}...` 
                : product.description
              }
            </Typography>
          )}

          {/* Pricing Display */}
          <Box sx={{ mb: 2 }}>
            {pricingLoading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="body2">Calculating price...</Typography>
              </Box>
            ) : pricing ? (
              <Typography variant="h6" color="primary" fontWeight="bold">
                {formatPrice(pricing.price)}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Select options to see price
              </Typography>
            )}
          </Box>

          {/* Package Info */}
          {pricing?.packageInfo && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                {pricing.packageInfo['Units Per Box'] && `${pricing.packageInfo['Units Per Box']} units per box`}
                {pricing.packageInfo['box size'] && ` • ${pricing.packageInfo['box size']}`}
              </Typography>
            </Box>
          )}
        </CardContent>

        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button
            variant="outlined"
            startIcon={<ViewIcon />}
            onClick={handleViewProduct}
            fullWidth
            sx={{ mr: 1 }}
          >
            View Details
          </Button>
          <Button
            variant="contained"
            startIcon={<ShoppingCartIcon />}
            onClick={handleViewProduct}
            disabled={loading}
            fullWidth
          >
            {loading ? <CircularProgress size={20} /> : 'Add to Cart'}
          </Button>
        </CardActions>
      </Card>

      {/* Product Details Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {product.name}
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Product Image */}
            <Grid size={{ xs: 12, md: 6 }}>
              <CardMedia
                component="img"
                height="300"
                image={getProductImage()}
                alt={product.name}
                sx={{ objectFit: 'cover', borderRadius: 1 }}
              />
            </Grid>

            {/* Product Options */}
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography variant="h6" gutterBottom>
                Configure Your Product
              </Typography>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Box sx={{ mb: 3 }}>
                  {options.map((optionGroup, index) => (
                    <FormControl key={index} fullWidth sx={{ mb: 2 }}>
                      <InputLabel>{optionGroup.group}</InputLabel>
                      <Select
                        value={selectedOptions[optionGroup.group] || ''}
                        onChange={(e) => handleOptionChange(optionGroup.group, e.target.value)}
                        label={optionGroup.group}
                      >
                        <MenuItem value="">
                          <em>Select {optionGroup.group}</em>
                        </MenuItem>
                        {optionGroup.options.map((option) => (
                          <MenuItem key={option.id} value={option.id}>
                            {option.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  ))}
                </Box>
              )}

              {/* Quantity */}
              <TextField
                label="Quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                inputProps={{ min: 1 }}
                fullWidth
                sx={{ mb: 2 }}
              />

              {/* Pricing Summary */}
              {pricing && (
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                  <Typography variant="h6" gutterBottom>
                    Pricing Summary
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Unit Price:</Typography>
                    <Typography fontWeight="bold">{formatPrice(pricing.price)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography>Quantity:</Typography>
                    <Typography>{quantity}</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="h6">Total:</Typography>
                    <Typography variant="h6" color="primary" fontWeight="bold">
                      {formatPrice(parseFloat(pricing.price) * quantity)}
                    </Typography>
                  </Box>
                </Paper>
              )}

              {/* Package Information */}
              {pricing?.packageInfo && (
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'info.50' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Package Information
                  </Typography>
                  {Object.entries(pricing.packageInfo).map(([key, value]) => (
                    <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" color="text.secondary">
                        {key}:
                      </Typography>
                      <Typography variant="body2">
                        {value}
                      </Typography>
                    </Box>
                  ))}
                </Paper>
              )}
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleAddToCart}
            disabled={isAddToCartDisabled()}
            startIcon={<ShoppingCartIcon />}
          >
            {pricingLoading ? <CircularProgress size={20} /> : 'Add to Cart'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ProductCard;
