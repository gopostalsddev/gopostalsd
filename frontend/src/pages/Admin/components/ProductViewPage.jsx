import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from "@mui/material";

import { fetchAllPrintProductsByCategory, updatePrintProductDetails } from "../../../services/product_service";
import logoImage from "../../../assets/logo.png";
import SpinnerOverlay from "../../../components/SpinnerOverlay";

const ProductViewPage = ({ category, onBack }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editForm, setEditForm] = useState({
    description: "",
    imageFile: null,
  });

  useEffect(() => {
    if (category) {
      loadProducts();
    }
  }, [category]);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await fetchAllPrintProductsByCategory(category.id);
      setProducts(data);
    } catch (error) {
      console.error("Failed to load products:", error);
      alert("Failed to load products!");
    } finally {
      setLoading(false);
    }
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setEditForm({
      description: product.description || "",
      imageFile: null,
    });
  };

  const handleSaveProduct = async () => {
    if (!editingProduct) return;

    try {
      setLoading(true);
      const success = await updatePrintProductDetails({
        id: editingProduct.id,
        description: editForm.description,
        imageFile: editForm.imageFile,
      });

      if (success) {
        await loadProducts(); // Reload products to get updated data
        setEditingProduct(null);
        setEditForm({ description: "", imageFile: null });
      } else {
        alert("Failed to update product!");
      }
    } catch (error) {
      console.error("Error updating product:", error);
      alert("Failed to update product!");
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setEditForm(prev => ({ ...prev, imageFile: file }));
    }
  };

  const getProductImage = (product) => {
    return product.image_url || logoImage;
  };

  const getProductDescription = (product) => {
    return product.description || "No description yet";
  };

  return (
    <Box sx={{ width: "100%", position: "relative" }}>
      <SpinnerOverlay loading={loading} />
      
      {/* Header */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexDirection: { xs: "column", sm: "row" },
          gap: 2,
          mb: 3,
        }}
      >
        <Typography 
          variant="h4"
          sx={{
            background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 700
          }}
        >
          {category.name}
        </Typography>
        <Button variant="outlined" onClick={onBack}>
          Back
        </Button>
      </Box>

      {/* Products Grid */}
      {products.length === 0 && !loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No products found in this category.
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3} sx={{ justifyContent: "center" }}>
          {products.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
            <Card
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                transition: "transform 0.2s ease",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: 4,
                },
                height: 500,
                width: 400
              }}
            >
              <Box
                sx={{
                  height: 250,
                  overflow: "hidden",
                  position: "relative",
                  flexShrink: 0,
                }}
              >
                <img
                  src={getProductImage(product)}
                  alt={product.name}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                  onError={(e) => {
                    e.target.src = logoImage;
                  }}
                />
              </Box>
              <CardContent sx={{ flexGrow: 1, display: "flex", flexDirection: "column", p: 2 }}>
                <Typography variant="h6" component="h3" gutterBottom sx={{ fontWeight: "bold" }}>
                  {product.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1, mb: 2, lineHeight: 1.5 }}>
                  {getProductDescription(product)}
                </Typography>
                <Box sx={{ mt: "auto" }}>
                  <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: "block" }}>
                    SKU: {product.sku}
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleEditProduct(product)}
                    sx={{ alignSelf: "flex-start" }}
                  >
                    Edit
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
        </Grid>
      )}

      {/* Edit Product Modal */}
      <Dialog
        open={Boolean(editingProduct)}
        onClose={() => setEditingProduct(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Edit Product: {editingProduct?.name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={4}
              value={editForm.description}
              onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
              <Typography variant="body2">Product Image:</Typography>
              <input
                accept="image/*"
                style={{ display: "none" }}
                id="product-image-upload"
                type="file"
                onChange={handleImageChange}
              />
              <label htmlFor="product-image-upload">
                <Button
                  variant="outlined"
                  component="span"
                  size="small"
                >
                  Upload Image
                </Button>
              </label>
              {editForm.imageFile && (
                <Typography variant="caption" color="primary">
                  {editForm.imageFile.name}
                </Typography>
              )}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingProduct(null)}>Cancel</Button>
          <Button onClick={handleSaveProduct} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductViewPage; 