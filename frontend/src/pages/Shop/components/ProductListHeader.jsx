import React, { useState, useEffect } from "react";
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  Button, 
  Grid, 
  CircularProgress, 
  Paper,
  Breadcrumbs,
  Chip,
  Divider
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Home as HomeIcon,
  Store as StoreIcon
} from '@mui/icons-material';

const ProductListHeader = ({productCategoryName, numberOfProducts, backToProductCategories}) => {

    return (
        <Box sx={{ mb: 4 }}>
            {/* Breadcrumbs */}
            <Breadcrumbs sx={{ mb: 3 }}>
                <Button
                    startIcon={<HomeIcon />}
                    onClick={backToProductCategories}
                    sx={{ textTransform: 'none', color: 'text.secondary' }}
                >
                    Shop
                </Button>
                <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
                    <StoreIcon sx={{ mr: 0.5, fontSize: 20 }} />
                    {productCategoryName}
                </Typography>
            </Breadcrumbs>

            {/* Main Header */}
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    flexDirection: { xs: "column", sm: "row" },
                    gap: 3,
                    mb: 3,
                }}
            >
                <Box sx={{ flex: 1 }}>
                    <Typography 
                        variant="h3" 
                        component="h1"
                        sx={{ 
                            fontWeight: 700, 
                            mb: 1,
                            background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}
                    >
                        {productCategoryName}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Chip
                            label={`${numberOfProducts} product types`}
                            color="primary"
                            variant="outlined"
                            size="small"
                        />
                        <Typography variant="body1" color="text.secondary">
                            Browse our collection of {productCategoryName.toLowerCase()} product types
                        </Typography>
                    </Box>
                </Box>

                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <Button 
                        variant="outlined" 
                        startIcon={<ArrowBackIcon />}
                        onClick={backToProductCategories}
                        sx={{
                            borderRadius: 2,
                            textTransform: 'none',
                            fontWeight: 600,
                            px: 3,
                            py: 1
                        }}
                    >
                        Back to Categories
                    </Button>
                </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />
        </Box>
    );
};

export default ProductListHeader