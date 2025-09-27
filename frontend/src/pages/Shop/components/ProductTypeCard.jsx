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
import {
  Category as CategoryIcon
} from '@mui/icons-material';
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
        boxShadow: 3,
        borderRadius: 3,
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: 8,
        }
      }}
    >
      {/* Product Type Image - Full Width */}
      <Box sx={{ position: 'relative', height: 200, m: 2 }}>
        <CardMedia
          component="img"
          height="200"
          image={displayImage}
          alt={productType?.name || 'Product Type'}
          sx={{
            objectFit: 'cover',
            borderRadius: 2,
            border: '1px solid #e0e0e0',
            transition: 'transform 0.3s ease',
            '&:hover': {
              transform: 'scale(1.05)'
            }
          }}
        />
        
        
        {/* Product Count Badge */}
        {!loading && !error && products.length > 0 && (
          <Chip
            label={`${products.length} products`}
            color="success"
            size="small"
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
              backgroundColor: 'rgba(76, 175, 80, 0.9)',
              color: 'white',
              fontWeight: 600
            }}
          />
        )}
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
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <CategoryIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography 
              variant="h5" 
              component="h2" 
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                lineHeight: 1.2
              }}
            >
              {productType?.name || 'Product Type'}
            </Typography>
          </Box>
          
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
              color: 'text.primary',
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            <CategoryIcon sx={{ fontSize: 16, color: 'primary.main' }} />
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
                          px: 2,
                          py: 1,
                          borderRadius: 2,
                          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          cursor: 'pointer',
                          border: '1px solid transparent',
                          position: 'relative',
                          overflow: 'hidden',
                          '&:hover': {
                            backgroundColor: 'primary.main',
                            border: '1px solid primary.dark',
                            transform: 'translateX(4px)',
                            boxShadow: '0 4px 12px rgba(25, 118, 210, 0.3)',
                            '& .MuiListItemText-primary': {
                              color: 'white',
                              fontWeight: 600
                            },
                            '&::before': {
                              opacity: 1,
                              transform: 'translateX(0)'
                            }
                          },
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '4px',
                            height: '100%',
                            backgroundColor: 'primary.light',
                            opacity: 0,
                            transform: 'translateX(-4px)',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                          }
                        }
                      }}
                    >
                      {products.map((product, index) => (
                        <ListItem 
                          key={product.id}
                          onClick={() => handleProductClick(product)}
                          sx={{
                            borderRadius: 2,
                            mb: 1,
                            border: '1px solid #e0e0e0',
                            backgroundColor: '#fafafa',
                            position: 'relative',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                            '&:hover': {
                              backgroundColor: 'primary.main',
                              border: '1px solid primary.dark',
                              transform: 'translateX(4px)',
                              boxShadow: '0 4px 12px rgba(7, 59, 102, 0.3)',
                              '& .MuiListItemText-primary': {
                                color: 'white',
                                fontWeight: 600
                              },
                              '&::before': {
                                opacity: 1,
                                transform: 'translateX(0)'
                              }
                            },
                            '&::before': {
                              content: '""',
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              width: '4px',
                              height: '100%',
                              backgroundColor: 'primary.light',
                              opacity: 0,
                              transform: 'translateX(-4px)',
                              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                            }
                          }}
                        >
                          <ListItemText
                            primary={product.name}
                            primaryTypographyProps={{
                              variant: 'body2',
                              sx: {
                                fontWeight: 500,
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                color: 'text.primary',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word',
                                hyphens: 'auto',
                                maxWidth: '100%',
                                position: 'relative',
                                pl: 1
                              }
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
          )}
        </Box>

      </CardContent>
    </Card>
  );
};

export default ProductTypeCard;
