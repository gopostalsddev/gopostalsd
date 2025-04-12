import React, { useState, useEffect } from "react";
import Navbar from "../components/NavBar";
import Footer from "../components/Footer";
import SpinnerOverlay from "../components/SpinnerOverlay"; // Import reusable component
import {
  Typography,
  Box,
  TableCell,
  Switch,
  Button,
  Table,
  TableBody,
  TableContainer,
  TableRow,
  Paper,
  TableHead,
  Select,
  MenuItem,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  fetchPrintProductCategories,
  updatePrintProductCategoryStatus,
  updatePrintProductCategoryDetails,
  syncPrintProductCategories,
} from "../services/product_service";

const AdminPage = () => {
  const [productCategories, setProductCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterMode, setFilterMode] = useState("All"); // Default filter mode
  const [startingLetter, setStartingLetter] = useState(""); // Default Category Name
  const [editingCategory, setEditingCategory] = useState(null);

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
    const updatedStatus = !currentStatus;
    const success = await updatePrintProductCategoryStatus(
      categoryId,
      updatedStatus
    );
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

  // Filtering Logic
  const filteredCategories = productCategories.filter((category) => {
    // Check for Enabled/Disabled/All Mode
    if (filterMode === "Enabled" && !category.enabled) return false;
    if (filterMode === "Disabled" && category.enabled) return false;

    // Check for Category Name
    if (startingLetter && !category.name.toLowerCase().startsWith(startingLetter.toLowerCase())) {
      return false;
    }

    return true;
  });

  const totalCategories = productCategories.length;
  const enabledCategories = productCategories.filter(
    (category) => category.enabled
  ).length;

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        position: "relative"
      }}
    >
      <Navbar />
      <SpinnerOverlay loading={loading} /> {/* Use reusable SpinnerOverlay */}
      <Box
        sx={{
          flex: 1,
          mt: "64px",
          p: 4,
    
        }}
      >
        <Header
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
          productCategories={filteredCategories} // Use filtered categories
          handleToggle={handleToggle}
          onEdit={(category) => setEditingCategory(category)}
        />
        <EditCategoryModal
          open={Boolean(editingCategory)}
          category={editingCategory}
          onClose={() => setEditingCategory(null)}
          onSave={async (updatedCategory) => {
            setLoading(true);
            const success = await updatePrintProductCategoryDetails(updatedCategory); // service function
            if (success) {
              await loadProductCategories();
            }
            setEditingCategory(null);
            setLoading(false);
          }}
        />
      </Box>
      <Footer />
    </Box>
  );
};

/** Header Component */
const Header = ({
  loading,
  handleSync,
  totalCategories,
  enabledCategories,
  filterMode,
  setFilterMode,
  startingLetter,
  setStartingLetter,
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
        {/* Main Title with Statistics */}
        <Typography variant="h4">Product Categories</Typography>
        <Typography variant="h4" sx={{ color: "text.secondary" }}>
          {enabledCategories}/{totalCategories}
        </Typography>
      </Box>
      <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        {/* Category Name Input */}
        <TextField
          label="Category Name"
          variant="outlined"
          size="small"
          value={startingLetter}
          onChange={(e) => setStartingLetter(e.target.value)}
        />
        {/* Filter Mode Select */}
        <Select
          value={filterMode}
          onChange={(e) => setFilterMode(e.target.value)}
          variant="outlined"
          size="small"
        >
          <MenuItem value="All">All</MenuItem>
          <MenuItem value="Enabled">Enabled</MenuItem>
          <MenuItem value="Disabled">Disabled</MenuItem>
        </Select>
        {/* Sync Button */}
        <Button
          variant="contained"
          color="primary"
          onClick={handleSync}
          disabled={loading}
        >
          Sync Categories
        </Button>
      </Box>
    </Box>
  );
};

/** ProductCategoryTable Component */
const ProductCategoryTable = ({ productCategories, handleToggle, onEdit }) => {
  return (
    <TableContainer component={Paper} sx={{ mt: 4, overflowX: "auto" }}>
      <Table>
        <TableHead>
          <TableRow sx={{ fontWeight: "bold", backgroundColor: "primary.main", color: "#fff"}}>
            <TableCell>
              <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Category</Typography>
            </TableCell>
            <TableCell>
            <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Enable</Typography>
            </TableCell>
            <TableCell>
            <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Details</Typography>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {productCategories.map((productCategory) => (
            <ProductCategoryTableRow
              key={productCategory.id}
              productCategory={productCategory}
              handleToggle={handleToggle}
              onEdit={onEdit}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

/** ProductCategoryTableRow Component */
const ProductCategoryTableRow = ({ productCategory, handleToggle, onEdit }) => {
  return (
    <TableRow sx={{ transition: 'transform 0.5s ease', '&:hover': { backgroundColor: '#eee' } }}>
      <TableCell>{productCategory.name}</TableCell>
      <TableCell>
        <Switch
          checked={productCategory.enabled}
          onChange={() => handleToggle(productCategory.id, productCategory.enabled)}
          color="primary"
        />
      </TableCell>
      <TableCell>
        <Button variant="outlined" size="small" onClick={() => onEdit(productCategory)}>
          Edit
        </Button>
      </TableCell>
    </TableRow>
  );
};

/** Modal For editing Category Details */
const EditCategoryModal = ({ open, category, onClose, onSave }) => {
  const [description, setDescription] = useState(category?.description || "");
  const [imageFile, setImageFile] = useState(null);

  useEffect(() => {
    if (category) {
      setDescription(category.description || "");
      setImageFile(null);
    }
  }, [category]);

  const handleSubmit = () => {
    onSave({ ...category, description, imageFile });
  };

  if (!category) return null;

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Edit Category</DialogTitle>
      <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
        <TextField
          label="Description"
          multiline
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          fullWidth
        />
        <input type="file" accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AdminPage;