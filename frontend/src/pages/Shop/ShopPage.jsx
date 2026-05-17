import React, { useState, useEffect } from "react";
import { Box, Typography, Card, CardContent, Button, Grid, CircularProgress, Paper } from '@mui/material';


// Import global components
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
    const  [productTypeCount, setProductTypeCount] = useState(0)
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
        setProductTypeCount(0);
    }

    const handleProductTypesLoaded = (count) => {
        setProductTypeCount(count);
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
        <SpinnerOverlay loading={loading} /> {/* Use SpinnerOverlay for loading state */}
        
        <Box sx={{ flex: 1, p: 4,}} >
          {selectedProduct ? (
            // If a product is selected, display product detail page
            <ProductDetailPage 
              product={selectedProduct} 
              onBack={handleBackToProducts} 
            />
          ) : selectedProductCategory ? (
            // If a category is selected, display its product types
            <Box sx={{ width: '100%', p: 0 }}>
              <ProductListHeader
                productCategoryName={selectedProductCategory ? selectedProductCategory.name : 'None'}
                numberOfProducts={productTypeCount}
                backToProductCategories={handleBackToProductCategories}
              />
              <ProductTypeList 
                category={selectedProductCategory} 
                onProductClick={handleViewProduct}
                onProductTypesLoaded={handleProductTypesLoaded}
              />
            </Box>
          ) : (
            // Display the enabled categories as cards
            <ProductCategoryList productCategories={productCategories} handleProductCategoryClick={handleProductCategoryClick} />
          )}
        </Box>
      </Box>
    );
};
  
export default ShopPage;
  
  

  