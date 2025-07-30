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
    Button
} from "@mui/material"

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

export default ProductCategoryTable