import React, { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Breadcrumbs
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CloudUpload as CloudUploadIcon,
  LocalShipping as LocalShippingIcon,
  ShoppingCart as ShoppingCartIcon,
  ArrowBack as ArrowBackIcon,
  Home as HomeIcon,
  Store as StoreIcon,
  Category as CategoryIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import {
  getShippingEstimates,
  addItemToCart,
  getOrCreateCart,
  fetchAllProductTypes
} from '../../../services/product_service';
import { useProductOptions } from '../../../hooks/useProductOptions';
import { useProductPricing } from '../../../hooks/useProductPricing';
import { formatPrice, calculateTotalPrice, getEstimatedShipDate } from '../../../utils/priceUtils';
import logoImage from '../../../assets/logo.png';

const ProductDetailPage = ({ product, onBack }) => {
  const [selectedOptions, setSelectedOptions] = useState({});
  const [quantity, setQuantity] = useState(1);
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [shippingInfo, setShippingInfo] = useState({
    country: 'US',
    state: 'CA',
    city: 'San Diego',
    zip: '92101'
  });
  const [shippingEstimates, setShippingEstimates] = useState([]);
  const [shippingLoading, setShippingLoading] = useState(false);
  const [showShippingDialog, setShowShippingDialog] = useState(false);
  const [error, setError] = useState(null);
  const [productTypeImage, setProductTypeImage] = useState(null);

  // Custom hooks for product options and pricing
  const { options, loading: optionsLoading, error: optionsError } = useProductOptions(product.vendor_product_id);
  const { pricing, loading: pricingLoading, error: pricingError } = useProductPricing(
    product.vendor_product_id, 
    selectedOptions, 
    options
  );

  // Combine errors from different sources
  const displayError = error || optionsError || pricingError;

  // Fetch product type image for fallback
  React.useEffect(() => {
    const fetchProductTypeImage = async () => {
      if (!product.type_id || product.type_id === 0) return;
      
      try {
        const result = await fetchAllProductTypes();
        if (result.success) {
          const productType = result.data.find(type => type.id === product.type_id);
          if (productType?.image) {
            setProductTypeImage(productType.image);
          }
        }
      } catch (err) {
        console.error('Error fetching product type image:', err);
      }
    };

    fetchProductTypeImage();
  }, [product.type_id]);

  const handleOptionChange = (group, optionId) => {
    setSelectedOptions(prev => ({
      ...prev,
      [group]: optionId
    }));
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleShippingEstimate = async () => {
    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please configure your product options first');
      return;
    }

    setShippingLoading(true);
    try {
      // Generate options in the correct format for Sinalite API
      const optionsObject = {};
      options.forEach(optionGroup => {
        const selectedId = selectedOptions[optionGroup.group];
        if (selectedId && selectedId !== '') {
          optionsObject[optionGroup.group] = selectedId;
        }
      });

      const items = [{
        productId: parseInt(product.vendor_product_id),
        options: optionsObject
      }];

      const estimates = await getShippingEstimates(items, shippingInfo);
      setShippingEstimates(estimates);
      setShowShippingDialog(true);
    } catch (error) {
      console.error('Error getting shipping estimates:', error);
      setError('Failed to get shipping estimates');
    } finally {
      setShippingLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please select all required options');
      return;
    }

    try {
      // Get or create cart
      const sessionId = `session_${Date.now()}`;
      const cart = await getOrCreateCart(sessionId, null, 6);
      
      if (!cart) {
        setError('Failed to create cart');
        return;
      }

      // Generate option IDs in the correct order
      const optionIds = options.map(optionGroup => 
        selectedOptions[optionGroup.group]
      ).filter(id => id && id !== '');

      const cartItem = await addItemToCart(
        cart.id,
        parseInt(product.vendor_product_id),
        product.name,
        product.sku,
        optionIds,
        quantity
      );

      if (cartItem) {
        setError(null);
        // Show success message or redirect
        alert('Item added to cart successfully!');
      } else {
        setError('Failed to add item to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      setError('Failed to add item to cart');
    }
  };

  const getTotalPrice = () => {
    return calculateTotalPrice(pricing?.price, quantity);
  };

  const steps = [
    'Configure Product',
    'Upload Artwork',
    'Shipping & Checkout'
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        {/* Breadcrumbs */}
        <Breadcrumbs sx={{ mb: 3 }}>
          <Button
            startIcon={<HomeIcon />}
            onClick={() => window.location.href = '/'}
            sx={{ textTransform: 'none', color: 'text.secondary' }}
          >
            Shop
          </Button>
          <Button
            startIcon={<StoreIcon />}
            onClick={onBack}
            sx={{ textTransform: 'none', color: 'text.secondary' }}
          >
            Product Types
          </Button>
          <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
            <CategoryIcon sx={{ mr: 0.5, fontSize: 20 }} />
            {product.name}
          </Typography>
        </Breadcrumbs>

        {/* Main Header */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexDirection: { xs: "column", sm: "row" },
            gap: 3,
            mb: 3,
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography 
              variant="h3" 
              component="h1"
              sx={{ 
                fontWeight: 700, 
                mb: 1,
                background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}
            >
              {product.name}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Typography variant="body1" color="text.secondary">
                {product.description}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Button 
              variant="outlined" 
              onClick={onBack}
              startIcon={<ArrowBackIcon />}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                px: 3,
                py: 1
              }}
            >
              Back to Products
            </Button>
          </Box>
        </Box>
      </Box>

      {displayError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {displayError}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Left Column - Product Image */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ textAlign: 'center' }}>
                <img
                  src={product.image || productTypeImage || logoImage}
                  alt={product.name}
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    height: 'auto',
                    borderRadius: '8px'
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Middle Column - Configuration */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, maxWidth: '450px', mx: 'auto' }}>
            <Typography variant="h5" gutterBottom>
              Price this item:
            </Typography>

            {optionsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ mb: 3 }}>
                {options.map((optionGroup, index) => (
                  <FormControl key={index} fullWidth sx={{ mb: 2 }}>
                    <InputLabel>{optionGroup.group}</InputLabel>
                    <Select
                      value={selectedOptions[optionGroup.group] || ''}
                      onChange={(e) => handleOptionChange(optionGroup.group, e.target.value)}
                      label={optionGroup.group}
                    >
                      <MenuItem value="">
                        <em>Select {optionGroup.group}</em>
                      </MenuItem>
                      {optionGroup.options.map((option) => (
                        <MenuItem key={option.id} value={option.id}>
                          {option.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ))}
              </Box>
            )}

            {/* Quantity */}
            <TextField
              label="Quantity"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              inputProps={{ min: 1 }}
              fullWidth
              sx={{ mb: 3 }}
            />

            {/* Pricing Display */}
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              {pricingLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">Calculating price...</Typography>
                </Box>
              ) : pricing ? (
                <Box>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Regular Price: {formatPrice(pricing.price)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Order now and this item is estimated to be ready to ship by {getEstimatedShipDate()} at 5 PM
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                    * Please note that this is just an estimate. Actual production time may vary.
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Select options to see price
                </Typography>
              )}
            </Box>

            {/* Package Information */}
            {pricing?.packageInfo && (
              <Accordion sx={{ mb: 3 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Package Information</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {Object.entries(pricing.packageInfo).map(([key, value]) => (
                      <ListItem key={key}>
                        <ListItemText
                          primary={key}
                          secondary={value}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<ShoppingCartIcon />}
                onClick={handleAddToCart}
                disabled={!pricing || pricingLoading}
                sx={{ flexGrow: 1 }}
              >
                Add to Cart
              </Button>
              <Button
                variant="outlined"
                startIcon={<LocalShippingIcon />}
                onClick={handleShippingEstimate}
                disabled={!pricing || shippingLoading}
              >
                {shippingLoading ? <CircularProgress size={20} /> : 'Estimate Shipping'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Right Column - Stepper for Additional Steps */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, maxWidth: '450px', mx: 'auto' }}>
            <Typography variant="h5" gutterBottom>
              Additional Steps:
            </Typography>
            <Stepper activeStep={activeStep} orientation="vertical">
              <Step>
                <StepLabel>Upload your artwork</StepLabel>
                <StepContent>
                  <Box sx={{ mb: 2 }}>
                    <input
                      accept="image/*,.pdf"
                      style={{ display: 'none' }}
                      id="file-upload"
                      multiple
                      type="file"
                      onChange={handleFileUpload}
                    />
                    <label htmlFor="file-upload">
                      <Button
                        variant="outlined"
                        component="span"
                        startIcon={<CloudUploadIcon />}
                        sx={{ mb: 2 }}
                      >
                        Upload Files
                      </Button>
                    </label>
                    
                    {uploadedFiles.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Uploaded Files:
                        </Typography>
                        {uploadedFiles.map((file, index) => (
                          <Chip
                            key={index}
                            label={file.name}
                            onDelete={() => removeFile(index)}
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                  <Button
                    variant="contained"
                    onClick={() => setActiveStep(1)}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    Continue
                  </Button>
                </StepContent>
              </Step>

              <Step>
                <StepLabel>Calculate shipping cost</StepLabel>
                <StepContent>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Enter your destination to get a shipping estimate.
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>Country</InputLabel>
                          <Select
                            value={shippingInfo.country}
                            onChange={(e) => setShippingInfo(prev => ({ ...prev, country: e.target.value }))}
                            label="Country"
                          >
                            <MenuItem value="US">United States</MenuItem>
                            <MenuItem value="CA">Canada</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <FormControl fullWidth>
                          <InputLabel>State/Province</InputLabel>
                          <Select
                            value={shippingInfo.state}
                            onChange={(e) => setShippingInfo(prev => ({ ...prev, state: e.target.value }))}
                            label="State/Province"
                          >
                            <MenuItem value="CA">California</MenuItem>
                            <MenuItem value="NY">New York</MenuItem>
                            <MenuItem value="TX">Texas</MenuItem>
                            <MenuItem value="ON">Ontario</MenuItem>
                            <MenuItem value="BC">British Columbia</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="City"
                          value={shippingInfo.city}
                          onChange={(e) => setShippingInfo(prev => ({ ...prev, city: e.target.value }))}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Zip/Postal Code"
                          value={shippingInfo.zip}
                          onChange={(e) => setShippingInfo(prev => ({ ...prev, zip: e.target.value }))}
                        />
                      </Grid>
                    </Grid>
                  </Box>
                  <Button
                    variant="contained"
                    onClick={handleShippingEstimate}
                    disabled={shippingLoading}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {shippingLoading ? <CircularProgress size={20} /> : 'Get a Quote'}
                  </Button>
                </StepContent>
              </Step>
            </Stepper>
          </Paper>
        </Grid>
      </Grid>

      {/* Shipping Estimates Dialog */}
      <Dialog
        open={showShippingDialog}
        onClose={() => setShowShippingDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Shipping Options
            <IconButton onClick={() => setShowShippingDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {shippingEstimates.length > 0 ? (
            <List>
              {shippingEstimates.map((option, index) => (
                <ListItem key={index} divider>
                  <ListItemIcon>
                    <LocalShippingIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={`${option.carrier_name} ${option.method_name}`}
                    secondary={`${option.shipping_days} - Days Shipping`}
                  />
                  <Typography variant="h6" color="primary">
                    {formatPrice(option.price)}
                  </Typography>
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography color="text.secondary">
              No shipping options available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowShippingDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProductDetailPage;
