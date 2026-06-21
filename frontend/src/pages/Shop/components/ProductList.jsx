import React, { useState, useEffect } from "react";
import { 
  Box, 
  Typography, 
  Grid, 
  CircularProgress, 
  Snackbar
} from '@mui/material';
import { fetchEnabledPrintProductsByCategory } from '../../../services/product_service';
import SpinnerOverlay from "../../../components/SpinnerOverlay";
import ProductCard from './ProductCard';

const ProductList = ({ category, onViewProduct }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState(new Set());
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [snackbarMessage, setSnackbarMessage] = useState('');

    useEffect(() => {
        const loadProducts = async () => {
            try {
                const fetchedProducts = await fetchEnabledPrintProductsByCategory(category.id);
                setProducts(fetchedProducts);
            } catch (error) {
                console.error("Error fetching products: ", error);
                setSnackbarMessage("Error loading products.");
                setSnackbarOpen(true);
            } finally {
                setLoading(false);
            }
        };

        loadProducts();
    }, [category]);

    const handleAddToCart = (cartItem) => {
        setSnackbarMessage(`${cartItem.product_name} added to cart!`);
        setSnackbarOpen(true);
    };

    const handleToggleFavorite = (productId) => {
        setFavorites(prev => {
            const newFavorites = new Set(prev);
            if (newFavorites.has(productId)) {
                newFavorites.delete(productId);
                setSnackbarMessage('Removed from favorites');
            } else {
                newFavorites.add(productId);
                setSnackbarMessage('Added to favorites');
            }
            setSnackbarOpen(true);
            return newFavorites;
        });
    };

    const handleCloseSnackbar = () => {
        setSnackbarOpen(false);
    };

    if (loading) {
        return (
            <Box sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '50vh' 
            }}>
                <CircularProgress size={60} />
            </Box>
        );
    }

    if (products.length === 0) {
        return (
            <Box sx={{ 
                textAlign: 'center', 
                py: 8,
                backgroundColor: '#fafafa',
                borderRadius: 2,
                border: '2px dashed #e0e0e0'
            }}>
                <Typography variant="h5" color="text.secondary" gutterBottom>
                    No products available
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    This category doesn't have any products yet.
                </Typography>
            </Box>
        );
    }

    return (
        <Box>
            <Grid 
                container 
                spacing={3}
                justifyContent="center"
                sx={{
                    alignItems: 'stretch', // This ensures all cards stretch to the same height
                }}
            >
                {products.map((product) => (
                    <Grid 
                        size={{ xs: 12, sm: 6, md: 4, lg: 3, xl: 2 }}
                        key={product.id}
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
                        <ProductCard
                            product={product}
                            onAddToCart={handleAddToCart}
                            onToggleFavorite={handleToggleFavorite}
                            isFavorite={favorites.has(product.id)}
                            onViewProduct={onViewProduct}
                        />
                    </Grid>
                ))}
            </Grid>
            
            <Snackbar
                open={snackbarOpen}
                autoHideDuration={3000}
                onClose={handleCloseSnackbar}
                message={snackbarMessage}
            />
        </Box>
    );
};

export default ProductList;