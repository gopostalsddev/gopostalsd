import React from "react";
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  CardMedia,
  Grid,
  Chip,
  Button,
  CardActions
} from '@mui/material';
import { 
  ArrowForward as ArrowForwardIcon,
  Store as StoreIcon
} from '@mui/icons-material';
import placeholderImage from '../../../assets/logo.png';

// ProductCategoryList Component
const ProductCategoryList = ({ productCategories, handleProductCategoryClick }) => {
  return (
    <Box sx={{ width: "100%", p: 0 }}>
      {/* Header Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography 
          variant="h3" 
          component="h1" 
          sx={{ 
            fontWeight: 700, 
            mb: 2,
            background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Our Product Categories
        </Typography>
        <Typography 
          variant="h6" 
          color="text.secondary" 
          sx={{ maxWidth: 600, mx: 'auto' }}
        >
          Discover our wide range of high-quality products organized by category
        </Typography>
      </Box>

      {/* Categories Grid */}
      <Grid 
        container 
        spacing={4}
        justifyContent="center"
        sx={{
          alignItems: 'stretch', // This ensures all cards stretch to the same height
        }}
      >
        {productCategories.map((category) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={4} 
            lg={3}
            xl={2}
            key={category.id}
            sx={{
              display: 'flex',
              alignItems: 'stretch', // Ensure grid items stretch to full height
              maxWidth: '400px', // Constrain maximum card width for categories
              '& > *': {
                width: '100%',
                height: '100%' // Ensure cards take full height of grid item
              }
            }}
          >
            <Card
              sx={{
                height: '100%',
                width: '100%',
                maxWidth: '400px', // Constrain card width
                display: 'flex',
                flexDirection: 'column',
                boxShadow: 3,
                cursor: "pointer",
                transition: "all 0.3s ease",
                borderRadius: 3,
                overflow: 'hidden',
                "&:hover": { 
                  transform: "translateY(-8px)",
                  boxShadow: 8,
                },
              }}
              onClick={() => handleProductCategoryClick(category)}
            >
              {/* Category Image */}
              <Box sx={{ position: 'relative', height: 250 }}>
                <CardMedia
                  component="img"
                  height="250"
                  image={category.image || placeholderImage}
                  alt={category.name}
                  sx={{
                    objectFit: "cover",
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.05)'
                    }
                  }}
                />
                
                {/* Overlay Gradient */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '50%',
                    background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
                  }}
                />
                
                {/* Category Status Badge */}
                {category.enabled && (
                  <Chip
                    label="Available"
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

              {/* Category Content */}
              <CardContent sx={{ 
                flexGrow: 1, 
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StoreIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography 
                      variant="h5" 
                      component="h2"
                      sx={{ 
                        fontWeight: 600,
                        color: 'text.primary',
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                        hyphens: 'auto',
                        maxWidth: '100%'
                      }}
                    >
                      {category.name}
                    </Typography>
                  </Box>
                  
                  {category.description && (
                    <Typography 
                      color="text.secondary" 
                      variant="body1"
                      sx={{ 
                        mb: 2,
                        lineHeight: 1.6,
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                        hyphens: 'auto',
                        maxWidth: '100%',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                    >
                      {category.description}
                    </Typography>
                  )}
                </Box>

                {/* Classification Status */}
                {category.product_classification_status && (
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={`${category.product_classification_status.classified_products || 0} products classified`}
                      size="small"
                      variant="outlined"
                      color="info"
                    />
                  </Box>
                )}
              </CardContent>

              {/* Action Button */}
              <CardActions sx={{ p: 3, pt: 0 }}>
                <Button
                  variant="contained"
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    width: '100%',
                    borderRadius: 2,
                    textTransform: 'none',
                    fontWeight: 600,
                    py: 1.5
                  }}
                >
                  Browse Products
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {productCategories.length === 0 && (
        <Box sx={{ 
          textAlign: 'center', 
          py: 8,
          backgroundColor: '#fafafa',
          borderRadius: 2,
          border: '2px dashed #e0e0e0'
        }}>
          <StoreIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No categories available
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Check back later for new product categories.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProductCategoryList;