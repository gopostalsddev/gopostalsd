import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Radio,
  RadioGroup,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Sync as SyncIcon,
} from "@mui/icons-material";
import {
  fetchAllProductTypes,
  createProductType,
  updateProductType,
  deleteProductType,
  fetchAllPrintProductsByCategory,
  assignProductToType,
  unassignProductFromType,
  updatePrintProductDetails,
  syncProductsForCategory,
} from "../../../services/product_service";
import SpinnerOverlay from "../../../components/SpinnerOverlay";
import logoImage from "../../../assets/logo.png";
import { CircularProgress } from "@mui/material";

const ProductClassificationView = ({ category, onBack, onCategoryUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [productTypes, setProductTypes] = useState([]);
  const [products, setProducts] = useState([]);
  const [localClassificationStatus, setLocalClassificationStatus] = useState(category.product_classification_status || {});
  
  // Product Type Management
  const [selectedProductType, setSelectedProductType] = useState("");
  const [creatingProductType, setCreatingProductType] = useState(false);
  const [productTypeForm, setProductTypeForm] = useState({
    name: "",
    description: "",
    imageFile: null,
  });
  
  // Product Management
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productForm, setProductForm] = useState({
    description: "",
    imageFile: null,
    assignToType: null,
  });

  // Load data when component mounts or category changes
  useEffect(() => {
    if (category.id) {
      setInitialLoading(true);
      loadData();
    }
  }, [category.id]);

  // Update local classification status when category prop changes
  useEffect(() => {
    // Only update local status if the category prop has a different classification status
    // This prevents overwriting our local updates
    if (JSON.stringify(category.product_classification_status) !== JSON.stringify(localClassificationStatus)) {
      setLocalClassificationStatus(category.product_classification_status || {});
    }
  }, [category.product_classification_status]);

  const loadData = async () => {
    try {
      setLoading(true);
      setInitialLoading(true);
      
      // Load product types and products in parallel
      const [typesResult, productsResult] = await Promise.all([
        fetchAllProductTypes(),
        fetchAllPrintProductsByCategory(category.id),
      ]);

      
      if (typesResult.success) {
        // Filter product types to only show those for the current category
        const categoryTypes = typesResult.data.filter(type => type.category_id === category.id);
        setProductTypes(categoryTypes);
        
        // Set default selected product type based on available types
        const availableTypes = categoryTypes.filter(type => type.id !== 0);
        if (availableTypes.length > 0) {
          // If there are product types available, select the first one as default
          setSelectedProductType(availableTypes[0].id);
        } else {
          // If no product types available, set to empty string (will show "None")
          setSelectedProductType("");
        }
        
      }
      
      if (productsResult.success) {
        setProducts(productsResult.data);
        updateLocalClassificationStatus(productsResult.data);
        
      }
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  };


  // Update local classification status based on current products
  const updateLocalClassificationStatus = (currentProducts) => {
    const totalProducts = currentProducts.length;
    const classifiedProducts = currentProducts.filter(p => p.type_id > 0).length;
    const allClassified = totalProducts > 0 && classifiedProducts === totalProducts;
    
    const newStatus = {
      total_products: totalProducts,
      classified_products: classifiedProducts,
      all_classified: allClassified
    };
    
    setLocalClassificationStatus(newStatus);
  };

  // Drag and Drop handlers
  const handleDragStart = (e, product) => {
    e.dataTransfer.setData("productId", product.id);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    if (!selectedProductType) {
      alert("Please select a product type first");
      return;
    }

    const productId = parseInt(e.dataTransfer.getData("productId"));
    const product = products.find(p => p.id === productId);
    
    if (product) {
      try {
        setLoading(true);
        
        await assignProductToType(productId, selectedProductType);
        
        // Update local state immediately for better UX
        const updatedProducts = products.map(p => 
          p.id === productId ? { ...p, type_id: selectedProductType } : p
        );
        setProducts(updatedProducts);
        updateLocalClassificationStatus(updatedProducts);
        
        //alert(`Product "${product.name}" has been classified to "${productTypes.find(t => t.id === selectedProductType)?.name}"`);
      } catch (error) {
        console.error("Error assigning product via drag & drop:", error);
        alert("Failed to classify product!");
        
        // If there was an error, revert the local state
        const revertedProducts = products.map(p => 
          p.id === productId ? { ...p, type_id: product.type_id } : p
        );
        setProducts(revertedProducts);
        updateLocalClassificationStatus(revertedProducts);
      } finally {
        setLoading(false);
      }
    }
  };

  // Product Type handlers
  const handleCreateProductType = async () => {
    if (!productTypeForm.name || !productTypeForm.description) {
      alert("Name and description are required!");
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("name", productTypeForm.name);
      formData.append("category_id", category.id);
      formData.append("description", productTypeForm.description);
      
      if (productTypeForm.imageFile) {
        formData.append("image", productTypeForm.imageFile);
      }

      const result = await createProductType(formData);
      setCreatingProductType(false);
      setProductTypeForm({ name: "", description: "", imageFile: null });
      
      // Add the new product type to local state
      if (result && result.id) {
        const newProductType = {
          id: result.id,
          name: result.name,
          description: result.description,
          image: result.image,
          category_id: category.id
        };
        setProductTypes(prev => [...prev, newProductType]);
      }
      
      // Don't call onCategoryUpdate here - the local state is already updated
      // The parent will get updated when the user navigates back
    } catch (error) {
      console.error("Failed to create product type:", error);
      alert("Failed to create product type!");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProductType = async () => {
    if (!editingProduct) return;

    try {
      setLoading(true);
      const formData = new FormData();
      if (productForm.description) {
        formData.append("description", productForm.description);
      }
      if (productForm.imageFile) {
        formData.append("image", productForm.imageFile);
      }

      await updateProductType(editingProduct.id, {
        description: productForm.description,
        imageFile: productForm.imageFile,
      });
      
      // Update local state immediately
      setProductTypes(prev => prev.map(type => 
        type.id === editingProduct.id 
          ? { ...type, description: productForm.description || type.description }
          : type
      ));
      
      setEditingProduct(null);
      setProductForm({ description: "", imageFile: null, assignToType: null });
      
      // Don't call onCategoryUpdate here - the local state is already updated
      // The parent will get updated when the user navigates back
    } catch (error) {
      console.error("Failed to update product type:", error);
      alert("Failed to update product type!");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProductType = async (typeId) => {
    if (!confirm("Are you sure you want to delete this product type?")) return;

    try {
      setLoading(true);
      await deleteProductType(typeId);
      
      // Update local state immediately
      setProductTypes(prev => prev.filter(type => type.id !== typeId));
      
      // If the deleted type was selected, clear the selection
      if (selectedProductType === typeId) {
        setSelectedProductType("");
      }
      
      // Don't call onCategoryUpdate here - the local state is already updated
      // The parent will get updated when the user navigates back
    } catch (error) {
      console.error("Failed to delete product type:", error);
      alert("Failed to delete product type!");
    } finally {
      setLoading(false);
    }
  };

  // Filter out the unclassified type (ID 0) from product type options
  const filteredProductTypes = productTypes.filter(type => type.id !== 0);

  // Product handlers
  const handleEditProduct = (product) => {
    setSelectedProduct(product);
    setProductForm({
      description: product.description || "",
      imageFile: null,
      assignToType: product.type_id === 0 ? null : product.type_id, // Convert 0 to null for UI
    });
  };

  const handleUpdateProduct = async () => {
    if (!selectedProduct) return;

    try {
      setLoading(true);
      
      // Handle product type assignment if changed
      if (productForm.assignToType !== selectedProduct.type_id) {
        if (productForm.assignToType) {
          // Assign to a specific type
          await assignProductToType(selectedProduct.id, productForm.assignToType);
          
          // Update local state immediately
          const updatedProducts = products.map(p => 
            p.id === selectedProduct.id ? { ...p, type_id: productForm.assignToType } : p
          );
          setProducts(updatedProducts);
          updateLocalClassificationStatus(updatedProducts);
        } else if (selectedProduct.type_id && selectedProduct.type_id !== 0) {
          // Unassign from current type (but not from unclassified)
          await unassignProductFromType(selectedProduct.id);
          
          // Update local state immediately
          const updatedProducts = products.map(p => 
            p.id === selectedProduct.id ? { ...p, type_id: 0 } : p
          );
          setProducts(updatedProducts);
          updateLocalClassificationStatus(updatedProducts);
        }
        // If assignToType is null/empty and current type is 0, no action needed
      }

      // Update product details
      const formData = new FormData();
      if (productForm.description) {
        formData.append("description", productForm.description);
      }
      if (productForm.imageFile) {
        formData.append("image", productForm.imageFile);
      }

      await updatePrintProductDetails({
        id: selectedProduct.id,
        description: productForm.description,
        imageFile: productForm.imageFile,
      });
      
      setSelectedProduct(null);
      setProductForm({ description: "", imageFile: null, assignToType: null });
      
      // Don't call onCategoryUpdate here - let the local state handle the UI
      // The parent will get updated when the user navigates back or when we explicitly need to sync
    } catch (error) {
      console.error("Failed to update product:", error);
      alert("Failed to update product!");
    } finally {
      setLoading(false);
    }
  };

  const getProductTypeName = (typeId) => {
    if (typeId === 0) {
      return "Unclassified";
    }
    const type = productTypes.find(t => t.id === typeId);
    return type ? type.name : "Unknown";
  };

  const getProductImage = (item) => {
    return item.image || logoImage;
  };

  const getProductDescription = (item) => {
    return item.description || "No description yet";
  };

  const isProductClassified = (product) => {
    return product.type_id > 0; // type_id = 0 is unclassified
  };

  const selectedType = productTypes.find(t => t.id === selectedProductType);
  const productsInSelectedType = selectedType 
    ? products.filter(p => p.type_id === selectedProductType)
    : [];

  // Function to sync changes with parent when navigating back
  const handleBackWithSync = () => {
    // Call onCategoryUpdate to ensure parent has latest data
    if (onCategoryUpdate) onCategoryUpdate();
    // Then navigate back
    onBack();
  };

  const handleSyncProducts = async () => {
    if (!confirm("Are you sure you want to sync products for this category? This will re-fetch and update all products from Sinalite API.")) {
      return;
    }
    
    try {
      setLoading(true);
    const syncResult = await syncProductsForCategory(category.id);
      
      // Show detailed sync results
      const message = `Sync completed successfully!\n\n` +
        `Products added: ${syncResult.products_added || 0}\n` +
        `Products updated: ${syncResult.products_updated || 0}\n` +
        `Total products: ${syncResult.total_products || 0}`;
      
      alert(message);
      
      // Reload data to show updated products from sync
      await loadData();
      
      // Update parent component
      if (onCategoryUpdate) {
        onCategoryUpdate();
      }
      
    } catch (error) {
      console.error("Error syncing products:", error);
      const errorMessage = error.response?.data?.error || error.message || "Failed to sync products";
      alert(`Sync failed: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // Show loading spinner while initial data is being fetched
  if (initialLoading) {
    return (
      <Box sx={{ 
        width: "100%", 
        height: "60vh", 
        display: "flex", 
        flexDirection: "column",
        alignItems: "center", 
        justifyContent: "center",
        gap: 2
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Loading product classification data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", position: "relative" }}>
      <SpinnerOverlay loading={loading} />
      
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexDirection: { xs: "column", sm: "row" },
          gap: 3,
          mb: 4,
          p: 3,
          backgroundColor: "#fafafa",
          borderRadius: 2,
          border: "1px solid #e0e0e0",
        }}
      >
        <Box sx={{ flex: 1 }}>
          <Typography 
            variant="h4" 
            sx={{ 
              mb: 2,
              fontWeight: 700,
              background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: "flex",
              alignItems: "center",
              gap: 2
            }}
          >
            {category.name}
            {localClassificationStatus && (
              <Chip
                label={`${localClassificationStatus.classified_products || 0}/${localClassificationStatus.total_products || 0} classified`}
                color={localClassificationStatus.all_classified ? "success" : "warning"}
                variant="filled"
                size="medium"
                sx={{ 
                  borderRadius: 2,
                  fontWeight: 600,
                  fontSize: "0.875rem"
                }}
              />
            )}
            <Button
              variant="outlined"
              size="small"
              onClick={handleSyncProducts}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SyncIcon />}
              sx={{
                borderRadius: 2,
                px: 2,
                py: 0.5,
                fontWeight: 500,
                borderWidth: 1.5,
                fontSize: "0.75rem",
                textTransform: "none",
                "&:hover": {
                  borderWidth: 2,
                  transform: "translateY(-1px)",
                  boxShadow: 1,
                },
                transition: "all 0.2s ease-in-out",
              }}
            >
              {loading ? "Syncing..." : "Sync Products"}
            </Button>
          </Typography>
          
          {localClassificationStatus && !localClassificationStatus.all_classified && (
            <Alert 
              severity="warning" 
              sx={{ 
                maxWidth: 500,
                borderRadius: 2,
                "& .MuiAlert-icon": {
                  alignItems: "center"
                }
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Please complete product classification before enabling this category.
              </Typography>
            </Alert>
          )}
        </Box>
        
        <Button 
          variant="outlined" 
          onClick={handleBackWithSync} 
          startIcon={<ArrowBackIcon />}
          sx={{
            borderRadius: 2,
            px: 3,
            py: 1.5,
            fontWeight: 500,
            borderWidth: 2,
            "&:hover": {
              borderWidth: 2,
              transform: "translateY(-1px)",
              boxShadow: 2,
            },
            transition: "all 0.2s ease-in-out",
          }}
        >
          Back to Categories
        </Button>
      </Box>

      {/* Product Types Section */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 2 }}>
        <Box sx={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          mb: 3,
          pb: 2,
          borderBottom: "1px solid #e0e0e0"
        }}>
          <Typography 
            variant="h5" 
            sx={{ 
              fontWeight: 600,
              background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              display: "flex",
              alignItems: "center",
              gap: 2
            }}
          >
            Product Types
            <Chip 
              label={filteredProductTypes.length === 0 
                ? "None available" 
                : `${filteredProductTypes.length} available`
              }
              size="small"
              color={filteredProductTypes.length === 0 ? "error" : "primary"}
              variant={filteredProductTypes.length === 0 ? "filled" : "outlined"}
            />
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setCreatingProductType(true)}
            sx={{
              borderRadius: 2,
              px: 3,
              py: 1.5,
              fontWeight: 500,
              boxShadow: 2,
              "&:hover": {
                boxShadow: 4,
                transform: "translateY(-1px)",
              },
              transition: "all 0.2s ease-in-out",
            }}
          >
            Add Product Type
          </Button>
        </Box>

        {/* Help message when no product types exist */}
        {filteredProductTypes.length === 0 && (
          <Alert 
            severity="info" 
            sx={{ 
              mb: 3,
              borderRadius: 2,
              "& .MuiAlert-icon": {
                alignItems: "center"
              }
            }}
          >
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              No product types found for this category. Create a product type first to start organizing your products.
            </Typography>
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Left Side - Product Type Selection and Details (1/4 width) */}
          <Grid item xs={12} md={3}>
            <Box sx={{ 
              width: { xs: "100%", sm: 600 },
              height: '100%', // Fixed height - never changes
              display: "flex",
              flexDirection: "column"
            }}>
              {/* Dropdown - Fixed at top */}
              <FormControl sx={{ mb: 3, width: "100%" }}>
                <InputLabel>Select Product Type</InputLabel>
                <Select
                  value={selectedProductType}
                  label="Select Product Type"
                  onChange={(e) => setSelectedProductType(e.target.value)}
                  displayEmpty
                  size="medium"
                >
                  <MenuItem value="">
                    {filteredProductTypes.length > 0 ? "" : ""}
                  </MenuItem>
                  {filteredProductTypes.map((type) => (
                    <MenuItem key={type.id} value={type.id}>
                      {type.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Product Type Card - Fixed Size Container */}
              <Box sx={{ 
                flex: 1, // Takes remaining space
                width: "100%",
                minHeight: 0 // Allow flex shrinking
              }}>
                {selectedType ? (
                  <Card sx={{ 
                    boxShadow: 2, 
                    borderRadius: 2,
                    height: "100%",
                    display: "flex",
                    flexDirection: "column"
                  }}>
                    <CardContent sx={{ 
                      p: 2.5, 
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between"
                    }}>
                      <Box sx={{ 
                        display: "flex", 
                        flexDirection: "row", 
                        alignItems: "center", 
                        mb: 3 
                      }}>
                        <Box
                          sx={{
                            width: { xs: 100, sm: 200, md: 220, lg: 240 },
                            height: { xs: 100, sm: 200, md: 220, lg: 240 },
                            borderRadius: 2,
                            overflow: "hidden",
                            mb: 2,
                            boxShadow: 1,
                            border: "2px solid #f0f0f0",
                            flexShrink: 0, // Prevent image from shrinking
                          }}
                        >
                          <img
                            src={getProductImage(selectedType)}
                            alt={selectedType.name}
                            style={{
                              width: "100%",
                              height: "100%",
                              objectFit: "cover",
                            }}
                          />
                        </Box>
                        <Box>
                        <Typography 
                          variant="h6" 
                          align="center" 
                          sx={{ 
                            mb: 1, 
                            fontWeight: 600,
                            color: "text.primary",
                            minHeight: "1.5em", // Fixed height for title
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                          }}
                        >
                          {selectedType.name}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.secondary" 
                          align="center"
                          sx={{ 
                            lineHeight: 1.4,
                            px: 1,
                            minHeight: "3em", // Fixed height for description
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                          }}
                        >
                          {getProductDescription(selectedType)}
                        </Typography>
                        </Box>
                      </Box>
                      <Box sx={{ 
                        display: "flex", 
                        gap: 1.5, 
                        justifyContent: "center",
                        flexWrap: "wrap",
                        mt: "auto" // Push buttons to bottom
                      }}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<EditIcon />}
                          onClick={() => {
                            setEditingProduct(selectedType);
                            setProductForm({
                              description: selectedType.description || "",
                              imageFile: null,
                              assignToType: null,
                            });
                          }}
                          sx={{ 
                            minWidth: 80,
                            borderRadius: 1.5
                          }}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          onClick={() => handleDeleteProductType(selectedType.id)}
                          sx={{ 
                            minWidth: 80,
                            borderRadius: 1.5
                          }}
                        >
                          Delete
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                ) : (
                  // Placeholder card when no type is selected - same dimensions
                  <Card sx={{ 
                    boxShadow: 1, 
                    borderRadius: 2,
                    height: "100%",
                    border: filteredProductTypes.length === 0 ? "2px solid #f44336" : "2px dashed #e0e0e0",
                    backgroundColor: filteredProductTypes.length === 0 ? "#ffebee" : "#fafafa"
                  }}>
                    <CardContent sx={{ 
                      p: 2.5, 
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center"
                    }}>
                      <Box sx={{ 
                        display: "flex", 
                        flexDirection: "column", 
                        alignItems: "center", 
                        mb: 3 
                      }}>
                        <Box
                          sx={{
                            width: 100,
                            height: 100,
                            borderRadius: 2,
                            mb: 2,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            backgroundColor: filteredProductTypes.length === 0 ? "#ffcdd2" : "#f0f0f0",
                            color: filteredProductTypes.length === 0 ? "#d32f2f" : "#999",
                            fontSize: "2rem"
                          }}
                        >
                          {filteredProductTypes.length > 0 ? "📋" : "➕"}
                        </Box>
                        <Typography 
                          variant="h6" 
                          align="center" 
                          sx={{ 
                            mb: 1, 
                            fontWeight: 600,
                            color: filteredProductTypes.length === 0 ? "error.main" : "text.secondary",
                            minHeight: "1.5em",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                          }}
                        >
                          {filteredProductTypes.length > 0 ? "No Type Selected" : "No Product Types"}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color={filteredProductTypes.length === 0 ? "error.main" : "text.disabled"}
                          align="center"
                          sx={{ 
                            lineHeight: 1.4,
                            px: 1,
                            minHeight: "3em",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                          }}
                        >
                          {filteredProductTypes.length > 0 
                            ? "Select a product type from the dropdown above to view its details and manage products."
                            : "Create a product type first to start organizing your products."
                          }
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Box>
            </Box>
          </Grid>

          {/* Right Side - Products in Selected Type (3/4 width) */}
          <Grid item xs={12} md={9}>
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 3, 
                fontWeight: 600,
                color: filteredProductTypes.length === 0 && !selectedType ? "error.main" : "text.primary",
                display: "flex",
                alignItems: "center",
                gap: 1
              }}
            >
              {selectedType 
                ? `Products In ${selectedType.name}`
                : filteredProductTypes.length === 0 
                  ? "No Product Types Available"
                  : "Products In Selected Type"
              }
              {selectedType && (
                <Chip 
                  label={`${productsInSelectedType.length} product${productsInSelectedType.length !== 1 ? 's' : ''}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
              {filteredProductTypes.length === 0 && (
                <Chip 
                  label="Create a product type first"
                  size="small"
                  color="error"
                  variant="filled"
                />
              )}
            </Typography>
            {selectedType ? (
              <Box
                sx={{
                  minHeight: 300,
                  border: "2px dashed #e0e0e0",
                  borderRadius: 3,
                  p: 3,
                  backgroundColor: "#fafafa",
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    borderColor: "#bdbdbd",
                    backgroundColor: "#f5f5f5",
                  }
                }}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 3, 
                    textAlign: "center",
                    fontSize: "0.9rem",
                    fontStyle: "italic"
                  }}
                >
                  💡 Drag products here to classify them to "{selectedType.name}"
                </Typography>
                {productsInSelectedType.length > 0 ? (
                  <List sx={{ p: 0 }}>
                    {productsInSelectedType.map((product, index) => (
                      <ListItem 
                        key={product.id} 
                        disablePadding
                        sx={{ 
                          mb: 1,
                          "&:last-child": { mb: 0 }
                        }}
                      >
                        <ListItemButton 
                          onClick={() => handleEditProduct(product)}
                          sx={{
                            borderRadius: 2,
                            border: "1px solid #e0e0e0",
                            backgroundColor: "white",
                            "&:hover": {
                              backgroundColor: "#f8f9fa",
                              borderColor: "#bdbdbd",
                              transform: "translateY(-1px)",
                              boxShadow: 2,
                            },
                            transition: "all 0.2s ease-in-out",
                          }}
                        >
                          <ListItemText
                            primary={
                              <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                                {product.name}
                              </Typography>
                            }
                            secondary={
                              <Typography variant="caption" color="text.secondary">
                                SKU: {product.sku}
                              </Typography>
                            }
                          />
                          <Chip
                            label="Classified"
                            color="success"
                            size="small"
                            sx={{ 
                              borderRadius: 1.5,
                              fontWeight: 500
                            }}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      py: 4,
                      color: "text.secondary"
                    }}
                  >
                    <Typography variant="body2" align="center" sx={{ mb: 1 }}>
                      No products assigned to this type yet.
                    </Typography>
                    <Typography variant="caption" align="center" color="text.disabled">
                      Drag products from the list below to classify them here.
                    </Typography>
                  </Box>
                )}
              </Box>
            ) : (
              <Box
                sx={{
                  minHeight: 300,
                  border: "2px dashed #e0e0e0",
                  borderRadius: 3,
                  p: 3,
                  backgroundColor: "#fafafa",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Box sx={{ textAlign: "center", color: "text.secondary" }}>
                  {filteredProductTypes.length === 0 ? (
                    <>
                      <Typography variant="body2" sx={{ mb: 1, color: "error.main" }}>
                        No product types available for this category
                      </Typography>
                      <Typography variant="caption" color="error.main">
                        Create a product type first to start organizing products.
                      </Typography>
                    </>
                  ) : (
                    <>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        Select a product type to view its products
                      </Typography>
                      <Typography variant="caption" color="text.disabled">
                        and enable drag & drop classification.
                      </Typography>
                    </>
                  )}
                </Box>
              </Box>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Products Section */}
      <Paper sx={{ p: 3 }}>
        <Typography 
          variant="h5" 
          sx={{ 
            mb: 3,
            fontWeight: 600,
            background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            display: "flex",
            alignItems: "center",
            gap: 2
          }}
        >
          All Products
          <Chip 
            label={`${products.length} total`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Typography>
        
        {products.length === 0 ? (
          <Box sx={{ 
            textAlign: "center", 
            py: 6, 
            color: "text.secondary",
            border: "2px dashed #e0e0e0",
            borderRadius: 3,
            backgroundColor: "#fafafa"
          }}>
            <Typography variant="h6" sx={{ mb: 2, color: "text.primary" }}>
              No products found for this category
            </Typography>
            <Typography variant="body2" sx={{ mb: 3 }}>
              {filteredProductTypes.length === 0 
                ? "Create a product type first, then sync products from the API."
                : "Use the 'Sync Products' button above to fetch products from the API."
              }
            </Typography>
            {filteredProductTypes.length === 0 && (
              <Button
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={() => setCreatingProductType(true)}
                sx={{ mr: 2 }}
              >
                Create Product Type
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={handleSyncProducts}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : <SyncIcon />}
            >
              {loading ? "Syncing..." : "Sync Products"}
            </Button>
          </Box>
        ) : (
          <Box
            sx={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 2.5,
              alignItems: 'stretch', // This ensures all cards stretch to the same height
            }}
          >
            {products.map((product) => (
              <Box
                key={product.id}
                sx={{
                  flex: '1 1 300px', // flex-grow: 1, flex-shrink: 1, flex-basis: 300px
                  minWidth: '300px',
                  maxWidth: '400px',
                  display: 'flex',
                  alignItems: 'stretch', // Ensure cards stretch to full height
                  '& > *': {
                    width: '100%',
                    height: '100%' // Ensure cards take full height of container
                  }
                }}
              >
                <Card 
                  sx={{ 
                    height: '100%',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    cursor: "pointer",
                    border: isProductClassified(product) ? "2px solid #4caf50" : "2px solid #f44336",
                    borderRadius: 2.5,
                    boxShadow: 1,
                    flex: 1, // Take full available space
                    "&:hover": {
                      boxShadow: 4,
                      transform: "translateY(-3px)",
                      transition: "all 0.3s ease-in-out",
                      borderColor: isProductClassified(product) ? "#2e7d32" : "#d32f2f",
                    },
                    transition: "all 0.2s ease-in-out",
                  }}
                  onClick={() => handleEditProduct(product)}
                  draggable
                  onDragStart={(e) => handleDragStart(e, product)}
                >
                  <CardContent sx={{ 
                    py: 2.5, 
                    px: 2.5,
                    flexGrow: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 1.5 }}>
                      <Typography 
                        variant="subtitle1" 
                        sx={{ 
                          fontWeight: 600,
                          color: "text.primary",
                          maxWidth: "70%",
                          wordWrap: 'break-word',
                          overflowWrap: 'break-word',
                          hyphens: 'auto',
                          lineHeight: 1.2
                        }}
                      >
                        {product.name}
                      </Typography>
                      <Chip
                        label={isProductClassified(product) ? "Classified" : "Unclassified"}
                        color={isProductClassified(product) ? "success" : "error"}
                        size="small"
                        sx={{ 
                          borderRadius: 1.5,
                          fontWeight: 500,
                          fontSize: "0.75rem"
                        }}
                      />
                    </Box>
                    
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        mb: 1,
                        fontSize: "0.875rem",
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                        hyphens: 'auto',
                        maxWidth: '100%'
                      }}
                    >
                      SKU: {product.sku}
                    </Typography>
                    
                    {isProductClassified(product) && (
                      <Box sx={{ mb: 1.5 }}>
                        <Chip
                          label={`Type: ${getProductTypeName(product.type_id)}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ 
                            borderRadius: 1.5,
                            fontSize: "0.75rem"
                          }}
                        />
                      </Box>
                    )}
                    
                    <Box sx={{ 
                      display: "flex", 
                      alignItems: "center", 
                      gap: 1,
                      mt: 2,
                      pt: 1.5,
                      borderTop: "1px solid #f0f0f0"
                    }}>
                      <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        sx={{ 
                          display: "flex",
                          alignItems: "center",
                          gap: 0.5,
                          fontSize: "0.75rem"
                        }}
                      >
                        💡 Click to edit
                      </Typography>
                      <Typography 
                        variant="caption" 
                        color="text.secondary"
                        sx={{ fontSize: "0.75rem" }}
                      >
                        •
                      </Typography>
                      <Typography 
                        variant="caption" 
                        color="text.secondary"
                        sx={{ 
                          display: "flex",
                          alignItems: "center",
                          gap: 0.5,
                          fontSize: "0.75rem"
                        }}
                      >
                        Drag to classify
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            ))}
          </Box>
        )}
      </Paper>

      {/* Create Product Type Dialog */}
      <Dialog open={creatingProductType} onClose={() => setCreatingProductType(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Product Type</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            variant="outlined"
            value={productTypeForm.name}
            onChange={(e) => setProductTypeForm({ ...productTypeForm, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={productTypeForm.description}
            onChange={(e) => setProductTypeForm({ ...productTypeForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setProductTypeForm({ ...productTypeForm, imageFile: e.target.files[0] })}
            style={{ marginBottom: 16 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatingProductType(false)}>Cancel</Button>
          <Button onClick={handleCreateProductType} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Product Type Dialog */}
      <Dialog open={!!editingProduct} onClose={() => setEditingProduct(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Product Type</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={productForm.description}
            onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setProductForm({ ...productForm, imageFile: e.target.files[0] })}
            style={{ marginBottom: 16 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingProduct(null)}>Cancel</Button>
          <Button onClick={handleUpdateProductType} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Product Dialog */}
      <Dialog open={!!selectedProduct} onClose={() => setSelectedProduct(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Product: {selectedProduct?.name}</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={productForm.description}
            onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setProductForm({ ...productForm, imageFile: e.target.files[0] })}
            style={{ marginBottom: 16 }}
          />
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="h6" sx={{ mb: 2 }}>
            Product Classification
          </Typography>
          <FormControl component="fieldset">
            <RadioGroup
              value={productForm.assignToType || ""}
              onChange={(e) => setProductForm({ ...productForm, assignToType: e.target.value || null })}
            >
              <FormControlLabel
                value=""
                control={<Radio />}
                label="Unclassified (No Product Type)"
              />
              {filteredProductTypes.map((type) => (
                <FormControlLabel
                  key={type.id}
                  value={type.id}
                  control={<Radio />}
                  label={type.name}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedProduct(null)}>Cancel</Button>
          <Button onClick={handleUpdateProduct} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductClassificationView; 