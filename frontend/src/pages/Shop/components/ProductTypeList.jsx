import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Container
} from '@mui/material';
import { fetchProductTypesByCategory } from '../../../services/product_service';
import ProductTypeCard from './ProductTypeCard';

/**
 * ProductTypeList Component
 * 
 * Displays a grid of product type cards for a given category.
 * Features professional styling with symmetrical layout and performance optimization.
 * 
 * @param {Object} category - The product category
 * @param {Function} onProductClick - Callback when a product is clicked
 */
const ProductTypeList = ({ category, onProductClick }) => {
  const [productTypes, setProductTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadProductTypes = async () => {
      if (!category?.id) return;

      setLoading(true);
      setError(null);

      try {
        const result = await fetchProductTypesByCategory(category.id);
        if (result.success) {
          setProductTypes(result.data);
        } else {
          setError('Failed to load product types');
        }
      } catch (err) {
        console.error('Error loading product types:', err);
        setError('Failed to load product types');
      } finally {
        setLoading(false);
      }
    };

    loadProductTypes();
  }, [category?.id]);

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh'
        }}>
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  if (productTypes.length === 0) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box sx={{
          textAlign: 'center',
          py: 8,
          backgroundColor: '#fafafa',
          borderRadius: 3,
          border: '2px dashed #e0e0e0'
        }}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No Product Types Available
          </Typography>
          <Typography variant="body1" color="text.secondary">
            This category doesn't have any product types configured yet.
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            fontWeight: 600,
            color: 'primary.main',
            mb: 1
          }}
        >
          {category?.name || 'Product Types'}
        </Typography>
        <Typography 
          variant="body1" 
          color="text.secondary"
          sx={{ mb: 2 }}
        >
          Choose a product type to view available products
        </Typography>
      </Box>

      {/* Product Types Grid */}
      <Grid 
        container 
        spacing={3}
        justifyContent="center"
        sx={{
          alignItems: 'stretch', // This ensures all cards stretch to the same height
        }}
      >
        {productTypes.map((productType) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={4} 
            lg={3} 
            xl={2}
            key={productType.id}
            sx={{
              display: 'flex',
              alignItems: 'stretch', // Ensure grid items stretch to full height
              maxWidth: '350px', // Constrain maximum card width
              '& > *': {
                width: '100%',
                height: '100%' // Ensure cards take full height of grid item
              }
            }}
          >
            <ProductTypeCard
              productType={productType}
              onProductClick={onProductClick}
            />
          </Grid>
        ))}
      </Grid>

      {/* Summary */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Showing {productTypes.length} product type{productTypes.length !== 1 ? 's' : ''}
        </Typography>
      </Box>
    </Container>
  );
};

export default ProductTypeList;
