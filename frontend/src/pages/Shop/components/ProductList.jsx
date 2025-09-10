import React, { useState, useEffect } from "react";
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardMedia,
  Button, 
  Grid, 
  CircularProgress, 
  Paper,
  Chip,
  IconButton,
  CardActions,
  Rating,
  Divider
} from '@mui/material';
import { 
  ShoppingCart as ShoppingCartIcon,
  Favorite as FavoriteIcon,
  Visibility as ViewIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { fetchEnabledPrintProductsByCategory } from '../../../services/product_service';
import SpinnerOverlay from "../../../components/SpinnerOverlay";
import logoImage from '../../../assets/logo.png';


const ProductList = ({ category }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState(new Set());

    useEffect(() => {
        const loadProducts = async () => {
            try {
                const fetchedProducts = await fetchEnabledPrintProductsByCategory(category.id);
                setProducts(fetchedProducts);
            } catch (error) {
                console.error("Error fetching products: ", error);
                alert("Error loading products.");
            } finally {
                setLoading(false);
            }
        };

        loadProducts();
    }, [category]);

    const handleAddToCart = (product) => {
        // TODO: Implement add to cart functionality
        console.log('Add to cart:', product);
    };

    const handleToggleFavorite = (productId) => {
        setFavorites(prev => {
            const newFavorites = new Set(prev);
            if (newFavorites.has(productId)) {
                newFavorites.delete(productId);
            } else {
                newFavorites.add(productId);
            }
            return newFavorites;
        });
    };

    const handleViewProduct = (product) => {
        // TODO: Implement product detail view
        console.log('View product:', product);
    };

    const getProductImage = (product) => {
        return product.image || logoImage;
    };

    const formatPrice = (price) => {
        // TODO: Implement actual pricing logic
        return `$${(Math.random() * 100 + 10).toFixed(2)}`;
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
            <Grid container spacing={3}>
                {products.map((product) => (
                    <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                        <Card 
                            sx={{ 
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                boxShadow: 2,
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                    boxShadow: 6,
                                    transform: 'translateY(-4px)',
                                }
                            }}
                        >
                            {/* Product Image */}
                            <Box sx={{ position: 'relative' }}>
                                <CardMedia
                                    component="img"
                                    height="200"
                                    image={getProductImage(product)}
                                    alt={product.name}
                                    sx={{
                                        objectFit: 'cover',
                                        backgroundColor: '#f5f5f5'
                                    }}
                                />
                                {/* Favorite Button */}
                                <IconButton
                                    sx={{
                                        position: 'absolute',
                                        top: 8,
                                        right: 8,
                                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                                        '&:hover': {
                                            backgroundColor: 'rgba(255, 255, 255, 1)',
                                        }
                                    }}
                                    onClick={() => handleToggleFavorite(product.id)}
                                >
                                    <FavoriteIcon 
                                        color={favorites.has(product.id) ? 'error' : 'action'} 
                                    />
                                </IconButton>
                                
                                {/* Product Type Badge */}
                                {product.type_id && product.type_id > 0 && (
                                    <Chip
                                        label="Classified"
                                        size="small"
                                        color="success"
                                        sx={{
                                            position: 'absolute',
                                            bottom: 8,
                                            left: 8,
                                            backgroundColor: 'rgba(76, 175, 80, 0.9)',
                                            color: 'white'
                                        }}
                                    />
                                )}
                            </Box>

                            {/* Product Info */}
                            <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                                <Typography 
                                    variant="h6" 
                                    component="h3" 
                                    sx={{ 
                                        mb: 1,
                                        fontWeight: 600,
                                        lineHeight: 1.2,
                                        display: '-webkit-box',
                                        WebkitLineClamp: 2,
                                        WebkitBoxOrient: 'vertical',
                                        overflow: 'hidden'
                                    }}
                                >
                                    {product.name}
                                </Typography>
                                
                                <Typography 
                                    variant="body2" 
                                    color="text.secondary" 
                                    sx={{ mb: 1 }}
                                >
                                    SKU: {product.sku}
                                </Typography>

                                {/* Rating Placeholder */}
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                    <Rating 
                                        value={4.5} 
                                        precision={0.5} 
                                        size="small" 
                                        readOnly 
                                    />
                                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                                        (24)
                                    </Typography>
                                </Box>

                                {/* Price */}
                                <Typography 
                                    variant="h6" 
                                    color="primary" 
                                    sx={{ 
                                        fontWeight: 700,
                                        mb: 1
                                    }}
                                >
                                    {formatPrice(product.price)}
                                </Typography>

                                {/* Description */}
                                {product.description && (
                                    <Typography 
                                        variant="body2" 
                                        color="text.secondary"
                                        sx={{
                                            display: '-webkit-box',
                                            WebkitLineClamp: 2,
                                            WebkitBoxOrient: 'vertical',
                                            overflow: 'hidden',
                                            mb: 1
                                        }}
                                    >
                                        {product.description}
                                    </Typography>
                                )}
                            </CardContent>

                            {/* Action Buttons */}
                            <CardActions sx={{ p: 2, pt: 0 }}>
                                <Button
                                    variant="contained"
                                    startIcon={<ShoppingCartIcon />}
                                    onClick={() => handleAddToCart(product)}
                                    sx={{ 
                                        flexGrow: 1,
                                        borderRadius: 2,
                                        textTransform: 'none',
                                        fontWeight: 600
                                    }}
                                >
                                    Add to Cart
                                </Button>
                                <IconButton
                                    onClick={() => handleViewProduct(product)}
                                    sx={{
                                        backgroundColor: 'rgba(0, 0, 0, 0.04)',
                                        '&:hover': {
                                            backgroundColor: 'rgba(0, 0, 0, 0.08)',
                                        }
                                    }}
                                >
                                    <ViewIcon />
                                </IconButton>
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default ProductList