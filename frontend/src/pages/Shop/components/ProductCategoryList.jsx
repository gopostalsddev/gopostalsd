import React from "react";
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import placeholderImage from '../../../assets/logo.png';

// ProductCategoryList Component
const ProductCategoryList = ({ productCategories, handleProductCategoryClick }) => {
  return (
    <Box sx={{ width: "100%", p: 0 }}>
      <Grid container spacing={4}>
        {productCategories.map((category) => (
          <Grid key={category.id}>
            <Card
              sx={{
                minWidth: 275,
                boxShadow: 3,
                cursor: "pointer",
                transition: "transform 0.3s ease",
                "&:hover": { transform: "scale(1.05)" },
              }}
              onClick={() => handleProductCategoryClick(category)}
            >
              <Box sx={{ height: 200, overflow: "hidden" }}>
                <img
                  src={category.image || placeholderImage}
                  alt={category.name}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                    display: "block",
                  }}
                />
              </Box>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {category.name}
                </Typography>
                {category.description && (
                  <Typography color="text.secondary" variant="body2">
                    {category.description}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ProductCategoryList;