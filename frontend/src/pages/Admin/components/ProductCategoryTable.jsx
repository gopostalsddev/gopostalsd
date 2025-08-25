import {
    Typography,
    TableCell,
    Switch,
    Table,
    TableBody,
    TableContainer,
    TableRow,
    Paper,
    TableHead,
    Button,
    Box,
    Chip,
    Tooltip,
} from "@mui/material"
import { Assignment as AssignmentIcon, AssignmentTurnedIn as AssignmentTurnedInIcon } from "@mui/icons-material";

/** ProductCategoryTable Component */
const ProductCategoryTable = ({ productCategories, handleToggle, onEdit, onEditCategory }) => {
  return (
    <TableContainer component={Paper} sx={{ mt: 4, overflowX: "auto" }}>
      <Table>
        <TableHead>
          <TableRow sx={{ fontWeight: "bold", backgroundColor: "primary.main", color: "#fff"}}>
            <TableCell>
              <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Category</Typography>
            </TableCell>
            <TableCell>
              <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Status</Typography>
            </TableCell>
            <TableCell>
              <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Classification</Typography>
            </TableCell>
            <TableCell>
              <Typography sx={{ fontWeight: "bold", color: "#fff" }}>Actions</Typography>
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
              onEditCategory={onEditCategory}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
  
/** ProductCategoryTableRow Component */
const ProductCategoryTableRow = ({ productCategory, handleToggle, onEdit, onEditCategory }) => {
  const status = productCategory.product_classification_status || {};
  const isFullyClassified = status.all_classified || false;
  const totalProducts = status.total_products || 0;
  const classifiedProducts = status.classified_products || 0;

  return (
    <TableRow sx={{ transition: 'transform 0.5s ease', '&:hover': { backgroundColor: '#eee' } }}>
      <TableCell>
        <Typography variant="body1" sx={{ fontWeight: 500 }}>
          {productCategory.name}
        </Typography>
        {productCategory.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {productCategory.description}
          </Typography>
        )}
      </TableCell>
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Switch
            checked={productCategory.enabled}
            onChange={() => handleToggle(productCategory.id, productCategory.enabled)}
            color="primary"
            disabled={!isFullyClassified && !productCategory.enabled}
          />
          <Chip
            label={productCategory.enabled ? "Enabled" : "Disabled"}
            color={productCategory.enabled ? "success" : "default"}
            size="small"
            variant="outlined"
          />
        </Box>
      </TableCell>
      <TableCell>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isFullyClassified ? (
            <Chip
              icon={<AssignmentTurnedInIcon />}
              label={`${classifiedProducts}/${totalProducts} Classified`}
              color="success"
              size="small"
            />
          ) : (
            <Chip
              icon={<AssignmentIcon />}
              label={`${classifiedProducts}/${totalProducts} Classified`}
              color="warning"
              size="small"
            />
          )}
        </Box>
      </TableCell>
      <TableCell>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="View and manage product classification">
            <Button 
              variant="contained" 
              size="small" 
              onClick={() => onEdit(productCategory)}
              startIcon={<AssignmentIcon />}
            >
              Manage
            </Button>
          </Tooltip>
          <Tooltip title="Edit category details">
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => onEditCategory(productCategory)}
            >
              Edit
            </Button>
          </Tooltip>
        </Box>
      </TableCell>
    </TableRow>
  );
};

export default ProductCategoryTable