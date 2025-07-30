import {
    Typography,
    Box,
    Button,
    Select,
    MenuItem,
    TextField,
  } from "@mui/material";


/** Header Component */
const ProductCategoryHeader = ({
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
}

export default ProductCategoryHeader