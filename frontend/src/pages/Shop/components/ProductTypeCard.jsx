import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Chip,
  Alert,
  Skeleton
} from '@mui/material';
import { fetchProductsByType } from '../../../services/product_service';
import logoImage from '../../../assets/logo.png';

/**
 * ProductTypeCard Component
 * 
 * Displays a product type with its image, description, and list of products.
 * Features professional styling with symmetrical layout and performance optimization.
 * 
 * @param {Object} productType - The product type data
 * @param {Function} onProductClick - Callback when a product is clicked
 */
const ProductTypeCard = ({ productType, onProductClick }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProducts = async () => {
      if (!productType?.id) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const result = await fetchProductsByType(productType.id);
        if (result.success) {
          setProducts(result.data);
        } else {
          setError('Failed to load products');
        }
      } catch (err) {
        console.error('Error loading products for type:', err);
        setError('Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    loadProducts();
  }, [productType?.id]);

  const handleProductClick = (product) => {
    if (onProductClick) {
      onProductClick(product);
    }
  };

  // Use product type image or fallback to logo
  const displayImage = productType?.image || logoImage;

  return (
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
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          boxShadow: 8,
          transform: 'translateY(-4px)',
        }
      }}
    >
      {/* Product Type Image - Small Square */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center',
        p: 2,
        backgroundColor: '#f5f5f5'
      }}>
        <img
          src={displayImage}
          alt={productType?.name || 'Product Type'}
          style={{
            width: '100px',
            height: '100px',
            objectFit: 'cover',
            borderRadius: '8px',
            border: '2px solid #e0e0e0'
          }}
        />
      </Box>

      <CardContent sx={{ 
        flexGrow: 1, 
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}>
        {/* Product Type Header */}
        <Box sx={{ mb: 2 }}>
          <Typography 
            variant="h5" 
            component="h2" 
            sx={{ 
              fontWeight: 600,
              color: 'primary.main',
              mb: 1,
              lineHeight: 1.2
            }}
          >
            {productType?.name || 'Product Type'}
          </Typography>
          
          {productType?.description && (
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                lineHeight: 1.5,
                mb: 2,
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                hyphens: 'auto',
                maxWidth: '100%'
              }}
            >
              {productType.description}
            </Typography>
          )}
        </Box>

        {/* Products List */}
        <Box sx={{ flexGrow: 1, mt: 2 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              fontWeight: 600,
              mb: 1.5,
              color: 'text.primary'
            }}
          >
            Available Products ({products.length})
          </Typography>

          {loading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {[...Array(3)].map((_, index) => (
                <Skeleton 
                  key={index} 
                  variant="text" 
                  width="80%" 
                  height={24}
                  sx={{ borderRadius: 1 }}
                />
              ))}
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : products.length === 0 ? (
            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ fontStyle: 'italic' }}
            >
              No products available for this type
            </Typography>
          ) : (
            <List 
              dense 
              sx={{ 
                p: 0,
                '& .MuiListItem-root': {
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: '#e0e0e0', // Light gray background
                    border: '1px solid #757575', // Dark gray border
                    '& .MuiListItemText-primary': {
                      color: '#ffffff', // White text
                      fontWeight: 500
                    }
                  }
                }
              }}
            >
              {products.map((product) => (
                <ListItem 
                  key={product.id}
                  onClick={() => handleProductClick(product)}
                  sx={{
                    borderRadius: 1,
                    mb: 0.5,
                    border: '1px solid transparent', // Transparent border by default
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      backgroundColor: '#e0e0e0',
                      border: '1px solid #757575',
                      '& .MuiListItemText-primary': {
                        color: '#ffffff',
                        fontWeight: 500
                      }
                    }
                  }}
                >
                  <ListItemText
                    primary={product.name}
                    primaryTypographyProps={{
                      variant: 'body2',
                      sx: {
                        fontWeight: 400,
                        transition: 'all 0.2s ease',
                        color: 'text.primary',
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                        hyphens: 'auto',
                        maxWidth: '100%'
                      }
                    }}
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Box>

        {/* Product Count Chip - Always at bottom */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          {!loading && !error && products.length > 0 && (
            <Chip
              label={`${products.length} product${products.length !== 1 ? 's' : ''}`}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ 
                fontSize: '0.75rem',
                height: 24
              }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ProductTypeCard;
