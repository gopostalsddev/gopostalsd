import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';
import { fetchEnabledPrintProductsByCategory } from '../../../services/product_service';
import SpinnerOverlay from "../../../components/SpinnerOverlay";


const ProductList = ({ category }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadProducts = async () => {
        try {
            const fetchedProducts = await fetchEnabledPrintProductsByCategory(category.id);  // Fetch products by category id
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

    return (
        <Box>
        <SpinnerOverlay loading={loading} /> {/* Use SpinnerOverlay for loading state */}
        {loading ? null : products.length === 0 ? (
            <Typography>No products available in this category -.</Typography>
        ) : (
            <Grid container spacing={3}>
            {products.map((product) => (
                <Grid  key={product.id}>
                <Card sx={{ minWidth: 275, boxShadow: 3 }}>
                    <CardContent>
                    <Typography variant="h6">{product.name}</Typography>
                    {/* <Typography color="text.secondary">{product.sku}</Typography>
                    <Typography>{product.category}</Typography>
                    <Typography>{product.enabled ? 'Available' : 'Out of stock'}</Typography> */}
                    </CardContent>
                </Card>
                </Grid>
            ))}
            </Grid>
        )}
        </Box>
    );
};

export default ProductList