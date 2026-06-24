import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Stack,
  Alert,
  CircularProgress,
  Typography,
} from "@mui/material";
import {
  fetchAllVendors,
  fetchProductTypesByCategory,
  createManualVendorProduct,
} from "../../../services/product_service";

const EMPTY_FORM = {
  name: "",
  sku: "",
  description: "",
  image: "",
  category_id: "",
  vendor_id: "",
  type_id: "",
  vendor_product_id: "",
};

export default function AddProductModal({ open, onClose, categories, onSuccess }) {
  const [form, setForm] = useState(EMPTY_FORM);
  const [vendors, setVendors] = useState([]);
  const [productTypes, setProductTypes] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) {
      fetchAllVendors()
        .then((data) => setVendors(Array.isArray(data) ? data : []))
        .catch(() => setVendors([]));
    }
  }, [open]);

  useEffect(() => {
    if (!form.category_id) {
      setProductTypes([]);
      setForm((prev) => ({ ...prev, type_id: "" }));
      return;
    }
    fetchProductTypesByCategory(form.category_id)
      .then(({ data }) => setProductTypes(Array.isArray(data) ? data : []))
      .catch(() => setProductTypes([]));
    setForm((prev) => ({ ...prev, type_id: "" }));
  }, [form.category_id]);

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleClose = () => {
    setForm(EMPTY_FORM);
    setError("");
    onClose();
  };

  const handleSubmit = async () => {
    setError("");

    if (!form.name.trim()) { setError("Product name is required."); return; }
    if (!form.sku.trim()) { setError("SKU is required."); return; }
    if (!form.category_id) { setError("Category is required."); return; }
    if (!form.vendor_id) { setError("Vendor is required."); return; }

    setSubmitting(true);
    try {
      await createManualVendorProduct({
        name: form.name.trim(),
        sku: form.sku.trim(),
        description: form.description.trim() || undefined,
        image: form.image.trim() || undefined,
        category_id: Number(form.category_id),
        vendor_id: Number(form.vendor_id),
        type_id: form.type_id ? Number(form.type_id) : 0,
        vendor_product_id: form.vendor_product_id.trim() || undefined,
      });
      onSuccess?.();
      handleClose();
    } catch (err) {
      setError(err.message || "Failed to create product.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6" fontWeight={700}>
          Add Custom Product
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Create a product outside of the Sinalite catalog.
        </Typography>
      </DialogTitle>

      <DialogContent dividers>
        <Stack spacing={2.5} sx={{ pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}

          <TextField
            label="Product Name"
            value={form.name}
            onChange={handleChange("name")}
            required
            fullWidth
          />
          <TextField
            label="SKU"
            value={form.sku}
            onChange={handleChange("sku")}
            required
            fullWidth
          />
          <TextField
            label="Category"
            select
            value={form.category_id}
            onChange={handleChange("category_id")}
            required
            fullWidth
          >
            {categories.map((cat) => (
              <MenuItem key={cat.id} value={cat.id}>
                {cat.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Vendor"
            select
            value={form.vendor_id}
            onChange={handleChange("vendor_id")}
            required
            fullWidth
          >
            {vendors.length === 0 ? (
              <MenuItem disabled>No vendors found</MenuItem>
            ) : (
              vendors.map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))
            )}
          </TextField>
          <TextField
            label="Product Type (optional)"
            select
            value={form.type_id}
            onChange={handleChange("type_id")}
            fullWidth
            disabled={!form.category_id || productTypes.length === 0}
            helperText={!form.category_id ? "Select a category first" : ""}
          >
            <MenuItem value="">— None —</MenuItem>
            {productTypes.map((t) => (
              <MenuItem key={t.id} value={t.id}>
                {t.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Vendor Product ID (optional)"
            value={form.vendor_product_id}
            onChange={handleChange("vendor_product_id")}
            fullWidth
            helperText="The ID used by the vendor to identify this product"
          />
          <TextField
            label="Description (optional)"
            value={form.description}
            onChange={handleChange("description")}
            multiline
            rows={3}
            fullWidth
          />
          <TextField
            label="Image URL (optional)"
            value={form.image}
            onChange={handleChange("image")}
            fullWidth
          />
        </Stack>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button onClick={handleClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={submitting}
          startIcon={submitting ? <CircularProgress size={16} /> : null}
        >
          {submitting ? "Creating…" : "Create Product"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
