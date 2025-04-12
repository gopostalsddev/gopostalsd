import React, { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';
import placeholderImage from '../assets/image_placeholder.jpg';
import Navbar from '../components/NavBar';
import Footer from '../components/Footer';
import SpinnerOverlay from "../components/SpinnerOverlay";
import { fetchEnabledPrintProductCategories, fetchPrintProductsByCategory } from '../services/product_service';

const LandingPage = () => {

  const  [productCategories, setProductCategories] = useState([])
  const  [selectedProductCategory, setSelectedProductCategrory] = useState(null)
  const  [products, setProducts] = useState([])
  const  [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadProductCategories = async () => {
      try {
        const enabledProductCategories = await fetchEnabledPrintProductCategories();
        setProductCategories(enabledProductCategories)
      }catch {
        console.error("Error fetching product categories: ", error)
        alert("Error loading product categories")
      }finally{
        setLoading(false)
      }
    };  
    loadProductCategories();
  }, [])

  const handleProductCategoryClick = (productCategory) => {
    setSelectedProductCategrory(productCategory)
  }

  const handleBackToProductCategories = () => {
    setSelectedProductCategrory(null);
  }

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        position: "relative",
      }}
    >
      <Navbar />
      <SpinnerOverlay loading={loading} /> {/* Use SpinnerOverlay for loading state */}
      
      <Box
        sx={{
          flex: 1,
          mt: "64px",  // Ensures content starts below the Navbar
          p: 4,
        }}
      >
        
        {selectedProductCategory ? (
          // If a category is selected, display its products
          <Box sx={{ width: '100%', p: 0 }}>
            <ProductCategoryHeader
              productCategoryName={selectedProductCategory ? selectedProductCategory.name : 'None'}
              numberOfProducts={products.length}
              backToProductCategories = {handleBackToProductCategories}
            />
            <ProductList category={selectedProductCategory} />
          </Box>
        ) : (
          // Display the enabled categories as cards
          <Box sx={{ width: '100%', p: 0 }}>
            <Grid container spacing={4}>
              {productCategories.map((category) => (
                <Grid key={category.id}>
                  <Card
                    sx={{
                      minWidth: 275,
                      boxShadow: 3,
                      cursor: 'pointer',
                      transition: 'transform 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.05)',
                      },
                    }}
                    onClick={() => handleProductCategoryClick(category)}
                  >
                    <CardContent sx={{display: "flex", justifyContent: "center", alignContent: "center"}}>
                      <Typography variant="h5">{category.name}</Typography>
                      {/* <Typography color="text.secondary">{category.description || 'No description available'}</Typography> */}
                      <Typography color="text.secondary">{category.description}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Box>

      <Footer />
    </Box>
  );
};

export default LandingPage;


const ProductCategoryHeader = ({
  productCategoryName,
  backToProductCategories,
}) => {

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

// ProductList Component within the same file
const ProductList = ({ category }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const fetchedProducts = await fetchPrintProductsByCategory(category.name);  // Fetch products by category name
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
        <Typography>No products available in this category.</Typography>
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
