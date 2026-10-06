import React, { useState, useEffect, lazy, Suspense } from "react";
import { useSearchParams } from "react-router-dom";
import { Box, Alert, CircularProgress } from '@mui/material';
import { useArtwork } from '../../contexts/ArtworkContext';


// Import global components
import SpinnerOverlay from "../../components/SpinnerOverlay";

// Import local components
import ProductCategoryList from "./components/ProductCategoryList";
import ProductListHeader from "./components/ProductListHeader";
import ProductTypeList from "./components/ProductTypeList";
const ProductDetailPage = lazy(() => import('./components/ProductDetailPage'));

import { fetchEnabledPrintProductCategories } from '../../services/product_service';

const ShopPage = () => {
    const { clearArtwork } = useArtwork();

    const  [productCategories, setProductCategories] = useState([])
    const  [selectedProductCategory, setSelectedProductCategrory] = useState(null)
    const  [selectedProduct, setSelectedProduct] = useState(null)
    const  [productTypeCount, setProductTypeCount] = useState(0)
    const  [loading, setLoading] = useState(true)
    const [categoryNotice, setCategoryNotice] = useState('')
    const [searchParams, setSearchParams] = useSearchParams();

    useEffect(() => {
      const loadProductCategories = async () => {
        try {
          const enabledProductCategories = await fetchEnabledPrintProductCategories();
          if (enabledProductCategories.length > 0) {
            setProductCategories(enabledProductCategories)
            setCategoryNotice('')

            // Restore state from URL on load/back-forward navigation
            const catId = searchParams.get('category');
            if (catId) {
              const cat = enabledProductCategories.find(c => String(c.id) === catId);
              if (cat) {
                setSelectedProductCategrory(cat);
                // Don't restore the product selection — the full product object
                // (including vendor_product_id) is only available after the type
                // list loads, and we have no endpoint to fetch it by id alone.
                // Restoring to the type list is the next best UX.
              }
            }
          } else {
            setProductCategories([])
            setCategoryNotice('No product categories are currently available. An administrator must sync, classify, and enable catalog categories.')
          }
        } catch (error) {
          console.error("Error fetching product categories: ", error)
          setCategoryNotice('Unable to load categories. Make sure the backend API is running and try again.')
        }finally{
          setLoading(false)
        }
      };
      loadProductCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const handleProductCategoryClick = (productCategory) => {
      setSelectedProductCategrory(productCategory)
      setSearchParams({ category: productCategory.id });
    }

    const handleBackToProductCategories = () => {
        setSelectedProductCategrory(null);
        setSelectedProduct(null);
        setProductTypeCount(0);
        setSearchParams({});
    }

    const handleProductTypesLoaded = (count) => {
        setProductTypeCount(count);
    }

    const handleViewProduct = (product) => {
        setSelectedProduct(product);
        setSearchParams({ category: selectedProductCategory.id, product: product.id });
    }

    const handleBackToProducts = () => {
        clearArtwork();
        setSelectedProduct(null);
        setSearchParams({ category: selectedProductCategory.id });
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
            <Suspense fallback={<Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>}>
              <ProductDetailPage
                product={selectedProduct}
                onBack={handleBackToProducts}
                categoryImage={selectedProductCategory?.image}
              />
            </Suspense>
          ) : selectedProductCategory ? (
            // If a category is selected, display its product types
            <Box sx={{ width: '100%', p: 0 }}>
              <ProductListHeader
                productCategoryName={selectedProductCategory ? selectedProductCategory.name : 'None'}
                productCategoryImage={selectedProductCategory?.image}
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
  
  

