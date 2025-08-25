import React, { useState, useEffect } from "react";
import { Box } from "@mui/material";

// Import global components
import Navbar from "../../components/NavBar";
import Footer from "../../components/Footer";
import SpinnerOverlay from "../../components/SpinnerOverlay";

// Import local components
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

const AdminPage = () => {
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
    // Check if all products are classified before enabling
    if (!currentStatus) {
      const category = productCategories.find(cat => cat.id === categoryId);
      if (category && !category.product_classification_status?.all_classified) {
        alert("Please complete product classification before enabling this category.");
        return;
      }
    }

    const updatedStatus = !currentStatus;
    const success = await updatePrintProductCategoryStatus(categoryId, updatedStatus);
    if (success) {
      setProductCategories(
        productCategories.map((cat) =>
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

  const handleCategoryUpdate = () => {
    // Reload categories when returning from classification view
    loadProductCategories();
  };

  const filteredCategories = productCategories.filter((category) => {
    if (filterMode === "Enabled" && !category.enabled) return false;
    if (filterMode === "Disabled" && category.enabled) return false;
    if (startingLetter && !category.name.toLowerCase().startsWith(startingLetter.toLowerCase())) {
      return false;
    }
    return true;
  });

  const totalCategories = productCategories.length;
  const enabledCategories = productCategories.filter((category) => category.enabled).length;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh", position: "relative" }}>
      <Navbar />
      <SpinnerOverlay loading={loading} />
      <Box sx={{ flex: 1, mt: "64px", p: 4 }}>
        {selectedCategory ? (
          <ProductClassificationView
            category={selectedCategory}
            onBack={handleBackToCategories}
            onCategoryUpdate={handleCategoryUpdate}
          />
        ) : (
          
          <>
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
          </>
        )}
      </Box>
      <Footer />
    </Box>
  );
};

export default AdminPage;