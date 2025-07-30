import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';


// Import global components
import Navbar from "../../components/NavBar";
import Footer from "../../components/Footer";
import SpinnerOverlay from "../../components/SpinnerOverlay";

// Import local components
import ProductCategoryList from "./components/ProductCategoryList";
import ProductListHeader from "./components/ProductListHeader";
import ProductList from "./components/ProductList";

import { fetchEnabledPrintProductCategories } from '../../services/product_service';

const ShopPage = () => {

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
        
        <Box sx={{ flex: 1, mt: "64px", p: 4,}} >
          {selectedProductCategory ? (
            // If a category is selected, display its products
            <Box sx={{ width: '100%', p: 0 }}>
              <ProductListHeader
                productCategoryName={selectedProductCategory ? selectedProductCategory.name : 'None'}
                numberOfProducts={products.length}
                backToProductCategories = {handleBackToProductCategories}
              />
              <ProductList category={selectedProductCategory} />
            </Box>
          ) : (
            // Display the enabled categories as cards
            <ProductCategoryList productCategories={productCategories} handleProductCategoryClick={handleProductCategoryClick} />
          )}
        </Box>
        <Footer />
      </Box>
    );
};
  
export default ShopPage;
  
  

  