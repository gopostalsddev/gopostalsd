import React, { useState, useEffect } from "react";

import {TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button
} from "@mui/material";


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

  export default EditCategoryModal