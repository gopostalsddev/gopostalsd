import React, { useState, useEffect } from "react";
import { Box, Alert } from '@mui/material';


// Import global components
import SpinnerOverlay from "../../components/SpinnerOverlay";

// Import local components
import ProductCategoryList from "./components/ProductCategoryList";
import ProductListHeader from "./components/ProductListHeader";
import ProductTypeList from "./components/ProductTypeList";
import ProductDetailPage from "./components/ProductDetailPage";

import { fetchEnabledPrintProductCategories, fetchPrintProductCategories, syncPrintProductCategories } from '../../services/product_service';

const ShopPage = () => {

    const  [productCategories, setProductCategories] = useState([])
    const  [selectedProductCategory, setSelectedProductCategrory] = useState(null)
    const  [selectedProduct, setSelectedProduct] = useState(null)
    const  [productTypeCount, setProductTypeCount] = useState(0)
    const  [loading, setLoading] = useState(true)
    const [categoryNotice, setCategoryNotice] = useState('')
    const [syncAttempted, setSyncAttempted] = useState(false)
  
    useEffect(() => {
      const loadProductCategories = async () => {
        try {
          const enabledProductCategories = await fetchEnabledPrintProductCategories();
          if (enabledProductCategories.length > 0) {
            setProductCategories(enabledProductCategories)
            setCategoryNotice('')
          } else {
            // Fallback: show all categories when none are enabled yet.
            const allProductCategories = await fetchPrintProductCategories();
            setProductCategories(allProductCategories)

            if (allProductCategories.length > 0) {
              setCategoryNotice('No categories are currently marked as enabled, so all available categories are being shown.')
            } else {
              if (!syncAttempted) {
                setSyncAttempted(true)
                setCategoryNotice('No categories found. Attempting an automatic catalog sync...')

                await syncPrintProductCategories();
                const categoriesAfterSync = await fetchPrintProductCategories();

                if (categoriesAfterSync.length > 0) {
                  setProductCategories(categoriesAfterSync)
                  setCategoryNotice('Categories were synced successfully. Showing all available categories.')
                } else {
                  setCategoryNotice('No product categories are available yet. Sync did not return categories. Please verify backend credentials and try sync from admin.')
                }
              } else {
                setCategoryNotice('No product categories are available yet. Please verify backend credentials and sync categories from admin.')
              }
            }
          }
        } catch (error) {
          console.error("Error fetching product categories: ", error)
          setCategoryNotice('Unable to load categories. Make sure the backend API is running and try again.')
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
          {categoryNotice && (
            <Alert severity="info" sx={{ mb: 3 }}>
              {categoryNotice}
            </Alert>
          )}
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
  
  

  