import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';

const ProductListHeader = ({productCategoryName, backToProductCategories}) => {

    return (
        <Box
        sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexDirection: { xs: "column", sm: "row" },
            gap: 2,
            mb: 2,
        }}
        >
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {/* Main Title */}
            <Typography variant="h4">{productCategoryName}</Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            {/* Go back to categories Button */}
            <Button variant="outlined" onClick={backToProductCategories}>
                Back
            </Button>
        </Box>
        </Box>
    );
};

export default ProductListHeader