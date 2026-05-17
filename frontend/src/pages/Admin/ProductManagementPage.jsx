import React, { useState, useEffect } from "react";
import { Box, Typography, Stack } from "@mui/material";

import SpinnerOverlay from "../../components/SpinnerOverlay";
import ProductCategoryHeader from "./components/ProductCategoryHeader";
import ProductCategoryTable from "./components/ProductCategoryTable";
import EditCategoryModal from "./components/EditCategoryModal";
import ProductClassificationView from "./components/ProductClassificationView";

import {
  fetchPrintProductCategories,
  updatePrintProductCategoryStatus,
  updatePrintProductCategoryDetails,
  syncPrintProductCategories,
} from "../../services/product_service";

const ProductManagementPage = () => {
  const [productCategories, setProductCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterMode, setFilterMode] = useState("All");
  const [startingLetter, setStartingLetter] = useState("");
  const [editingCategory, setEditingCategory] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  useEffect(() => {
    loadProductCategories();
  }, []);

  const loadProductCategories = async () => {
    try {
      setLoading(true);
      const data = await fetchPrintProductCategories();
      setProductCategories(data);
    } catch (error) {
      console.error("Failed to load product categories:", error);
      alert("Failed to load product categories!");
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (categoryId, currentStatus) => {
    if (!currentStatus) {
      const category = productCategories.find((cat) => cat.id === categoryId);
      if (category && !category.product_classification_status?.all_classified) {
        alert("Please complete product classification before enabling this category.");
        return;
      }
    }

    const updatedStatus = !currentStatus;
    const success = await updatePrintProductCategoryStatus(categoryId, updatedStatus);
    if (success) {
      setProductCategories((prevCategories) =>
        prevCategories.map((cat) =>
          cat.id === categoryId ? { ...cat, enabled: updatedStatus } : cat
        )
      );
    }
  };

  const handleSync = async () => {
    setLoading(true);
    await syncPrintProductCategories();
    await loadProductCategories();
    setLoading(false);
  };

  const handleCategoryAction = (category) => {
    setSelectedCategory(category);
  };

  const handleBackToCategories = () => {
    setSelectedCategory(null);
  };

  const handleCategoryUpdate = async () => {
    await loadProductCategories();
  };

  const filteredCategories = productCategories.filter((category) => {
    if (filterMode === "Enabled" && !category.enabled) return false;
    if (filterMode === "Disabled" && category.enabled) return false;
    if (
      startingLetter &&
      !category.name.toLowerCase().startsWith(startingLetter.toLowerCase())
    ) {
      return false;
    }
    return true;
  });

  const totalCategories = productCategories.length;
  const enabledCategories = productCategories.filter((category) => category.enabled)
    .length;

  return (
    <Box
      sx={{
        flex: 1,
        position: "relative",
        backgroundColor: (theme) => theme.palette.grey[50],
        py: { xs: 4, md: 6 },
      }}
    >
      <SpinnerOverlay loading={loading} />
      <Box
        sx={{
          maxWidth: "1300px",
          mx: "auto",
          px: { xs: 3, md: 6 },
        }}
      >
        {selectedCategory ? (
          <ProductClassificationView
            category={selectedCategory}
            onBack={handleBackToCategories}
            onCategoryUpdate={handleCategoryUpdate}
          />
        ) : (
          <Stack spacing={4}>
            <Box>
              <Typography variant="h4" fontWeight={700} gutterBottom>
                Product Management
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Control the storefront catalog, align categories with vendor data, and keep your product library ready for launch.
              </Typography>
            </Box>

            <ProductCategoryHeader
              loading={loading}
              handleSync={handleSync}
              totalCategories={totalCategories}
              enabledCategories={enabledCategories}
              filterMode={filterMode}
              setFilterMode={setFilterMode}
              startingLetter={startingLetter}
              setStartingLetter={setStartingLetter}
            />
            <ProductCategoryTable
              productCategories={filteredCategories}
              handleToggle={handleToggle}
              onEdit={handleCategoryAction}
              onEditCategory={(category) => setEditingCategory(category)}
            />
            <EditCategoryModal
              open={Boolean(editingCategory)}
              category={editingCategory}
              onClose={() => setEditingCategory(null)}
              onSave={async (updatedCategory) => {
                setLoading(true);
                const success = await updatePrintProductCategoryDetails(updatedCategory);
                if (success) await loadProductCategories();
                setEditingCategory(null);
                setLoading(false);
              }}
            />
          </Stack>
        )}
      </Box>
    </Box>
  );
};

export default ProductManagementPage;

