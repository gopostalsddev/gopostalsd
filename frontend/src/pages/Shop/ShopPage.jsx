import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';


// Import global components
import Navbar from "../../components/NavBar";
import Footer from "../../components/Footer";
import SpinnerOverlay from "../../components/SpinnerOverlay";

// Import local components
import ProductCategoryList from "./components/ProductCategoryList";
import ProductListHeader from "./components/ProductListHeader";
import ProductTypeList from "./components/ProductTypeList";
import ProductDetailPage from "./components/ProductDetailPage";

import { fetchEnabledPrintProductCategories } from '../../services/product_service';

const ShopPage = () => {

    const  [productCategories, setProductCategories] = useState([])
    const  [selectedProductCategory, setSelectedProductCategrory] = useState(null)
    const  [selectedProduct, setSelectedProduct] = useState(null)
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
        setSelectedProduct(null);
    }

    const handleViewProduct = (product) => {
        setSelectedProduct(product);
    }

    const handleBackToProducts = () => {
        setSelectedProduct(null);
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
          {selectedProduct ? (
            // If a product is selected, display product detail page
            <ProductDetailPage 
              product={selectedProduct} 
              onBack={handleBackToProducts} 
            />
          ) : selectedProductCategory ? (
            // If a category is selected, display its product types
            <ProductTypeList 
              category={selectedProductCategory} 
              onProductClick={handleViewProduct}
            />
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
  
  

  