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
  Breadcrumbs,
  Snackbar,
  CardMedia,
  Checkbox,
  FormControlLabel
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
  Close as CloseIcon,
  Visibility as VisibilityIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import {
  getShippingEstimates,
  fetchAllProductTypes
} from '../../../services/product_service';
import { useCartOperations } from '../../../hooks/useCart';
import { useAuth } from '../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useProductOptions } from '../../../hooks/useProductOptions';
import { useProductPricing } from '../../../hooks/useProductPricing';
import { formatPrice, calculateTotalPrice, getEstimatedShipDate } from '../../../utils/priceUtils';
import logoImage from '../../../assets/logo.png';

const ProductDetailPage = ({ product, onBack }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { addItemToCart } = useCartOperations();
  const [selectedOptions, setSelectedOptions] = useState({});
  const [quantity, setQuantity] = useState(1);
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [fileError, setFileError] = useState(null);
  const [previewFiles, setPreviewFiles] = useState([]);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  const [shippingInfo, setShippingInfo] = useState({
    country: 'US',
    state: 'CA',
    city: 'San Diego',
    zip: '92101'
  });

  // State/province options based on country
  const getStateOptions = (country) => {
    if (country === 'US') {
      return [
        { value: 'AL', label: 'Alabama' },
        { value: 'AK', label: 'Alaska' },
        { value: 'AZ', label: 'Arizona' },
        { value: 'AR', label: 'Arkansas' },
        { value: 'CA', label: 'California' },
        { value: 'CO', label: 'Colorado' },
        { value: 'CT', label: 'Connecticut' },
        { value: 'DE', label: 'Delaware' },
        { value: 'FL', label: 'Florida' },
        { value: 'GA', label: 'Georgia' },
        { value: 'HI', label: 'Hawaii' },
        { value: 'ID', label: 'Idaho' },
        { value: 'IL', label: 'Illinois' },
        { value: 'IN', label: 'Indiana' },
        { value: 'IA', label: 'Iowa' },
        { value: 'KS', label: 'Kansas' },
        { value: 'KY', label: 'Kentucky' },
        { value: 'LA', label: 'Louisiana' },
        { value: 'ME', label: 'Maine' },
        { value: 'MD', label: 'Maryland' },
        { value: 'MA', label: 'Massachusetts' },
        { value: 'MI', label: 'Michigan' },
        { value: 'MN', label: 'Minnesota' },
        { value: 'MS', label: 'Mississippi' },
        { value: 'MO', label: 'Missouri' },
        { value: 'MT', label: 'Montana' },
        { value: 'NE', label: 'Nebraska' },
        { value: 'NV', label: 'Nevada' },
        { value: 'NH', label: 'New Hampshire' },
        { value: 'NJ', label: 'New Jersey' },
        { value: 'NM', label: 'New Mexico' },
        { value: 'NY', label: 'New York' },
        { value: 'NC', label: 'North Carolina' },
        { value: 'ND', label: 'North Dakota' },
        { value: 'OH', label: 'Ohio' },
        { value: 'OK', label: 'Oklahoma' },
        { value: 'OR', label: 'Oregon' },
        { value: 'PA', label: 'Pennsylvania' },
        { value: 'RI', label: 'Rhode Island' },
        { value: 'SC', label: 'South Carolina' },
        { value: 'SD', label: 'South Dakota' },
        { value: 'TN', label: 'Tennessee' },
        { value: 'TX', label: 'Texas' },
        { value: 'UT', label: 'Utah' },
        { value: 'VT', label: 'Vermont' },
        { value: 'VA', label: 'Virginia' },
        { value: 'WA', label: 'Washington' },
        { value: 'WV', label: 'West Virginia' },
        { value: 'WI', label: 'Wisconsin' },
        { value: 'WY', label: 'Wyoming' }
      ];
    } else if (country === 'CA') {
      return [
        { value: 'AB', label: 'Alberta' },
        { value: 'BC', label: 'British Columbia' },
        { value: 'MB', label: 'Manitoba' },
        { value: 'NB', label: 'New Brunswick' },
        { value: 'NL', label: 'Newfoundland and Labrador' },
        { value: 'NS', label: 'Nova Scotia' },
        { value: 'ON', label: 'Ontario' },
        { value: 'PE', label: 'Prince Edward Island' },
        { value: 'QC', label: 'Quebec' },
        { value: 'SK', label: 'Saskatchewan' },
        { value: 'NT', label: 'Northwest Territories' },
        { value: 'NU', label: 'Nunavut' },
        { value: 'YT', label: 'Yukon' }
      ];
    }
    return [];
  };
  const [shippingEstimates, setShippingEstimates] = useState([]);
  const [shippingLoading, setShippingLoading] = useState(false);
  const [showShippingDialog, setShowShippingDialog] = useState(false);
  const [error, setError] = useState(null);
  const [productTypeImage, setProductTypeImage] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [showSuccessSnackbar, setShowSuccessSnackbar] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Custom hooks for product options and pricing
  const { options, loading: optionsLoading, error: optionsError } = useProductOptions(product.vendor_product_id);
  const { pricing, loading: pricingLoading, error: pricingError } = useProductPricing(
    product.vendor_product_id, 
    selectedOptions, 
    options
  );

  const hasSelectedValue = (value) =>
    value !== undefined && value !== null && `${value}` !== '';

  // Manage initial loading state
  React.useEffect(() => {
    // Set initial loading to false when we have the basic product data
    // Don't wait for options and pricing to load - show the layout immediately
    if (product && product.vendor_product_id) {
      setInitialLoading(false);
    }
  }, [product]);

  // Set initial values when options load
  React.useEffect(() => {
    if (options && options.length > 0) {
      const initialSelections = {};
      options.forEach(optionGroup => {
        if (optionGroup.options && optionGroup.options.length > 0) {
          // Set the first option as the initial value
          initialSelections[optionGroup.group] = optionGroup.options[0].id;
        }
      });
      setSelectedOptions(initialSelections);
    }
  }, [options]);

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
    
    // Clear validation error for this field
    if (validationErrors[group]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[group];
        return newErrors;
      });
    }
  };

  const validateFile = (file) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    // Temporarily restrict to PDF only - uncomment image types below when ready
    const allowedTypes = ['application/pdf'];
    // const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf']; // Enable image support later
    
    if (file.size > maxSize) {
      return `File ${file.name} is too large. Maximum size is 10MB.`;
    }
    
    if (!allowedTypes.includes(file.type)) {
      return `File ${file.name} has an unsupported format. Please use PDF only.`;
    }
    
    return null;
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setFileError(null);
    
    const validFiles = [];
    const errors = [];
    
    files.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(error);
      } else {
        validFiles.push(file);
      }
    });
    
    if (errors.length > 0) {
      setFileError(errors.join(' '));
    }
    
    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...validFiles]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files);
      setFileError(null);
      
      const validFiles = [];
      const errors = [];
      
      files.forEach(file => {
        const error = validateFile(file);
        if (error) {
          errors.push(error);
        } else {
          validFiles.push(file);
        }
      });
      
      if (errors.length > 0) {
        setFileError(errors.join(' '));
      }
      
      if (validFiles.length > 0) {
        setUploadedFiles(prev => [...prev, ...validFiles]);
      }
    }
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    setFileError(null);
  };

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) {
      return '🖼️';
    } else if (file.type === 'application/pdf') {
      return '📄';
    }
    return '📎';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handlePreviewFiles = () => {
    if (uploadedFiles.length === 0) return;
    
    // Create preview data for images
    const previewData = uploadedFiles.map(file => ({
      file,
      url: URL.createObjectURL(file),
      approved: false
    }));
    
    setPreviewFiles(previewData);
    setShowPreviewDialog(true);
  };

  const handleApproveFile = (index) => {
    setPreviewFiles(prev => 
      prev.map((item, i) => 
        i === index ? { ...item, approved: !item.approved } : item
      )
    );
  };

  const handleConfirmApproval = () => {
    // Only keep approved files
    const approvedFiles = previewFiles
      .filter(item => item.approved)
      .map(item => item.file);
    
    setUploadedFiles(approvedFiles);
    setShowPreviewDialog(false);
    setPreviewFiles([]);
    
    // Clean up object URLs
    previewFiles.forEach(item => {
      URL.revokeObjectURL(item.url);
    });
  };

  const handleCancelPreview = () => {
    setShowPreviewDialog(false);
    // Clean up object URLs
    previewFiles.forEach(item => {
      URL.revokeObjectURL(item.url);
    });
    setPreviewFiles([]);
  };

  const handleShippingEstimate = async () => {
    if (!validateShippingInfo()) {
      setError('Please fill in all required shipping information');
      return;
    }

    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please configure your product options first');
      return;
    }

    setShippingLoading(true);
    setError(null);
    try {
      // Generate options in the correct format for Sinalite API
      const optionsObject = {};
      options.forEach(optionGroup => {
        const selectedId = selectedOptions[optionGroup.group];
        if (hasSelectedValue(selectedId)) {
          // Find the option name for the selected ID
          const selectedOption = optionGroup.options.find(opt => String(opt.id) === String(selectedId));
          if (selectedOption) {
            optionsObject[optionGroup.group] = selectedOption.id.toString();
          }
        }
      });

      // Format request according to Sinalite API documentation
      // Sinalite API expects options as an object with string values
      const requestData = {
        items: [{
          productId: parseInt(product.vendor_product_id),
          options: optionsObject  // Keep as object with string values
        }],
        shippingInfo: {
          ShipState: shippingInfo.state,
          ShipZip: shippingInfo.zip,
          ShipCountry: shippingInfo.country
        }
      };

      const estimates = await getShippingEstimates(requestData);
      setShippingEstimates(estimates);
      setShowShippingDialog(true);
    } catch (error) {
      console.error('Error getting shipping estimates:', error);
      setError(error?.response?.data?.error || 'Failed to get shipping estimates');
    } finally {
      setShippingLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!validateForm()) {
      setError('Please fix the validation errors before adding to cart');
      return;
    }

    if (!pricing) {
      setError('Please wait for pricing to load');
      return;
    }

    setError(null);
    setSuccessMessage(null);

    try {
      // Generate option IDs in the correct order
      const optionIds = options.map(optionGroup => 
        selectedOptions[optionGroup.group]
      ).filter(hasSelectedValue);

      // Check if quantity is part of API options
      const hasQuantityInOptions = options.some(optionGroup => 
        optionGroup.group.toLowerCase().includes('quantity') || 
        optionGroup.group.toLowerCase().includes('qty')
      );

      // Use quantity from API options if available, otherwise use local quantity
      const finalQuantity = hasQuantityInOptions ? 
        (selectedOptions.Quantity || selectedOptions.quantity || selectedOptions.Qty || 1) : 
        quantity;

      const result = await addItemToCart(
        parseInt(product.vendor_product_id),
        optionIds,
        finalQuantity
      );

      if (result.success) {
        setSuccessMessage(`Successfully added ${finalQuantity} ${finalQuantity > 1 ? 'items' : 'item'} to cart!`);
        setShowSuccessSnackbar(true);
        setRetryCount(0);
      } else {
        setError(result.error || 'Failed to add item to cart. Please try again.');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      const errorMessage = error.response?.data?.error || 'Failed to add item to cart. Please try again.';
      setError(errorMessage);
    }
  };

  const getTotalPrice = () => {
    return calculateTotalPrice(pricing?.price, quantity);
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    setError(null);
    // Trigger re-fetch of options and pricing
    window.location.reload();
  };

  const clearMessages = () => {
    setError(null);
    setSuccessMessage(null);
  };

  const validateForm = () => {
    const errors = {};
    
    // Validate required options
    if (options && options.length > 0) {
      options.forEach(optionGroup => {
        if (!hasSelectedValue(selectedOptions[optionGroup.group])) {
          errors[optionGroup.group] = `${optionGroup.group} is required`;
        }
      });
    }
    
    // Validate quantity only if it's not part of API options
    const hasQuantityInOptions = options.some(optionGroup => 
      optionGroup.group.toLowerCase().includes('quantity') || 
      optionGroup.group.toLowerCase().includes('qty')
    );
    
    if (!hasQuantityInOptions && quantity < 1) {
      errors.quantity = 'Quantity must be at least 1';
    }
    
    // Validate shipping info for shipping estimates
    if (activeStep >= 1) {
      if (!shippingInfo.city.trim()) {
        errors.city = 'City is required';
      }
      if (!shippingInfo.zip.trim()) {
        errors.zip = 'ZIP/Postal code is required';
      }
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateShippingInfo = () => {
    const errors = {};
    
    if (!shippingInfo.city.trim()) {
      errors.city = 'City is required';
    }
    if (!shippingInfo.zip.trim()) {
      errors.zip = 'ZIP/Postal code is required';
    }
    
    setValidationErrors(prev => ({ ...prev, ...errors }));
    return Object.keys(errors).length === 0;
  };

  const steps = [
    'Configure Product',
    'Upload Artwork',
    'Shipping & Checkout'
  ];

  // Show loading spinner while initial data is being fetched
  if (initialLoading) {
    return (
      <Box sx={{ 
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw", 
        height: "100vh", 
        display: "flex", 
        flexDirection: "column",
        alignItems: "center", 
        justifyContent: "center",
        gap: 2,
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        zIndex: 9999
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Loading product details...
        </Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 0 }}>
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
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography 
              variant="h3" 
              component="h1"
              sx={{ 
                fontWeight: 700, 
                mb: 1,
                fontSize: { xs: '1.75rem', sm: '2.125rem', md: '3rem' },
                background: 'linear-gradient(45deg,rgb(0, 0, 0),rgb(7, 59, 102))',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                wordBreak: 'break-word'
              }}
            >
              {product.name}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Typography 
                variant="body1" 
                color="text.secondary"
                sx={{ 
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                  lineHeight: 1.5
                }}
              >
                {product.description}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ 
            display: "flex", 
            alignItems: "center", 
            gap: 2,
            width: { xs: '100%', sm: 'auto' },
            justifyContent: { xs: 'flex-start', sm: 'flex-end' }
          }}>
            <Button 
              variant="outlined" 
              onClick={onBack}
              startIcon={<ArrowBackIcon />}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                px: 3,
                py: 1,
                width: { xs: '100%', sm: 'auto' }
              }}
            >
              Back to Products
            </Button>
          </Box>
        </Box>
      </Box>

      {displayError && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }} 
          onClose={clearMessages}
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Retry
            </Button>
          }
        >
          {displayError}
          {retryCount > 0 && (
            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
              Retry attempt: {retryCount}
            </Typography>
          )}
        </Alert>
      )}

      {successMessage && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={clearMessages}>
          {successMessage}
        </Alert>
      )}

      <Grid 
        container 
        spacing={3}
        justifyContent="center"
        sx={{
          alignItems: 'stretch', // This ensures all cards stretch to the same height
        }}
      >
        {/* Left Column - Product Image */}
        <Grid 
          size={{ xs: 12, lg: 4 }}
          sx={{
            display: 'flex',
            alignItems: 'stretch',
            maxWidth: '400px', // Constrain maximum width to match ProductTypes spacing
            '& > *': {
              width: '100%',
              height: '100%' // Ensure cards take full height of grid item
            }
          }}
        >
          <Card sx={{ height: 'fit-content', width: '100%' }}>
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
              
              {/* Product Description */}
              {product.description && (
                <Box sx={{ mt: 2, textAlign: 'left' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                    {product.description}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Middle Column - Configuration */}
        <Grid 
          size={{ xs: 12, lg: 4 }}
          sx={{
            display: 'flex',
            alignItems: 'stretch',
            maxWidth: '400px', // Constrain maximum width to match ProductTypes spacing
            '& > *': {
              width: '100%',
              height: '100%' // Ensure cards take full height of grid item
            }
          }}
        >
          <Paper sx={{ p: { xs: 2, sm: 3 }, width: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Price this item:
            </Typography>

            <Box sx={{ mb: 3 }}>
              {optionsLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                options.map((optionGroup, index) => (
                  <FormControl 
                    key={index} 
                    fullWidth 
                    sx={{ mb: 2 }}
                    error={!!validationErrors[optionGroup.group]}
                  >
                    <InputLabel>{optionGroup.group}</InputLabel>
                    <Select
                      value={selectedOptions[optionGroup.group] ?? ''}
                      onChange={(e) => handleOptionChange(optionGroup.group, e.target.value)}
                      label={optionGroup.group}
                    >
                      {optionGroup.options.map((option) => (
                        <MenuItem key={option.id} value={option.id}>
                          {option.name}
                        </MenuItem>
                      ))}
                    </Select>
                    {validationErrors[optionGroup.group] && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 1.75 }}>
                        {validationErrors[optionGroup.group]}
                      </Typography>
                    )}
                  </FormControl>
                ))
              )}
            </Box>

            {/* Quantity - Only show if not included in API options */}
            {!options.some(optionGroup => 
              optionGroup.group.toLowerCase().includes('quantity') || 
              optionGroup.group.toLowerCase().includes('qty')
            ) && (
              <TextField
                label="Quantity"
                type="number"
                value={quantity}
                onChange={(e) => {
                  const newQuantity = Math.max(1, parseInt(e.target.value) || 1);
                  setQuantity(newQuantity);
                  // Clear validation error
                  if (validationErrors.quantity) {
                    setValidationErrors(prev => {
                      const newErrors = { ...prev };
                      delete newErrors.quantity;
                      return newErrors;
                    });
                  }
                }}
                inputProps={{ min: 1 }}
                fullWidth
                sx={{ mb: 3 }}
                error={!!validationErrors.quantity}
                helperText={validationErrors.quantity}
              />
            )}

            {/* Pricing Display */}
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              {pricingLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">Calculating price...</Typography>
                </Box>
              ) : pricing ? (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="h6" color="primary">
                      Unit Price: {formatPrice(pricing.price)}
                    </Typography>
                    {quantity > 1 && (
                      <Typography variant="body2" color="text.secondary">
                        × {quantity}
                      </Typography>
                    )}
                  </Box>
                  
                  {quantity > 1 && (
                    <Box sx={{ borderTop: '1px solid', borderColor: 'divider', pt: 1, mt: 1 }}>
                      <Typography variant="h5" color="primary" sx={{ fontWeight: 700 }}>
                        Total: {formatPrice(getTotalPrice())}
                      </Typography>
                    </Box>
                  )}
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
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
            <Box sx={{ 
              display: 'flex', 
              gap: 2, 
              flexWrap: 'wrap',
              flexDirection: { xs: 'column', sm: 'row' }
            }}>
              <Button
                variant="contained"
                startIcon={<ShoppingCartIcon />}
                onClick={handleAddToCart}
                disabled={!pricing || pricingLoading}
                sx={{ 
                  flexGrow: 1,
                  minHeight: { xs: '48px', sm: 'auto' }
                }}
                size="large"
              >
                Add to Cart
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Right Column - Stepper for Additional Steps */}
        <Grid 
          size={{ xs: 12, lg: 4 }}
          sx={{
            display: 'flex',
            alignItems: 'stretch',
            maxWidth: '400px', // Constrain maximum width to match ProductTypes spacing
            '& > *': {
              width: '100%',
              height: '100%' // Ensure cards take full height of grid item
            }
          }}
        >
          <Paper sx={{ p: { xs: 2, sm: 3 }, width: '100%' }}>
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
                    
                    {/* Drag and Drop Area */}
                    <Box
                      onDragEnter={handleDrag}
                      onDragLeave={handleDrag}
                      onDragOver={handleDrag}
                      onDrop={handleDrop}
                      sx={{
                        border: `2px dashed ${dragActive ? 'primary.main' : 'grey.300'}`,
                        borderRadius: 2,
                        p: 3,
                        textAlign: 'center',
                        bgcolor: dragActive ? 'primary.50' : 'grey.50',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          bgcolor: 'primary.50',
                          borderColor: 'primary.main'
                        }
                      }}
                      onClick={() => document.getElementById('file-upload').click()}
                    >
                      <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                      <Typography variant="h6" gutterBottom>
                        {dragActive ? 'Drop files here' : 'Drag & drop files here'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        or click to browse files
                      </Typography>
                      <Button
                        variant="outlined"
                        component="span"
                        startIcon={<CloudUploadIcon />}
                      >
                        Choose Files
                      </Button>
                      <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                        Supported format: PDF only (Max 10MB each)
                      </Typography>
                    </Box>
                    
                    {/* File Error Display */}
                    {fileError && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        {fileError}
                      </Alert>
                    )}
                    
                    {/* Uploaded Files Display */}
                    {uploadedFiles.length > 0 && (
                      <Box sx={{ mt: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                          <Typography variant="subtitle2">
                            Uploaded Files ({uploadedFiles.length}):
                          </Typography>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<VisibilityIcon />}
                            onClick={handlePreviewFiles}
                            sx={{ textTransform: 'none' }}
                          >
                            Preview & Approve
                          </Button>
                        </Box>
                        <List dense>
                          {uploadedFiles.map((file, index) => (
                            <ListItem
                              key={index}
                              sx={{
                                border: '1px solid',
                                borderColor: 'divider',
                                borderRadius: 1,
                                mb: 1,
                                bgcolor: 'background.paper'
                              }}
                            >
                              <ListItemIcon>
                                <Typography sx={{ fontSize: 20 }}>
                                  {getFileIcon(file)}
                                </Typography>
                              </ListItemIcon>
                              <ListItemText
                                primary={file.name}
                                secondary={formatFileSize(file.size)}
                              />
                              <IconButton
                                edge="end"
                                onClick={() => removeFile(index)}
                                size="small"
                              >
                                <CloseIcon />
                              </IconButton>
                            </ListItem>
                          ))}
                        </List>
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
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <FormControl fullWidth>
                          <InputLabel>Country</InputLabel>
                          <Select
                            value={shippingInfo.country}
                            onChange={(e) => {
                              const newCountry = e.target.value;
                              const stateOptions = getStateOptions(newCountry);
                              setShippingInfo(prev => ({ 
                                ...prev, 
                                country: newCountry,
                                state: stateOptions.length > 0 ? stateOptions[0].value : ''
                              }));
                            }}
                            label="Country"
                          >
                            <MenuItem value="US">United States</MenuItem>
                            <MenuItem value="CA">Canada</MenuItem>
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <FormControl fullWidth>
                          <InputLabel>State/Province</InputLabel>
                          <Select
                            value={shippingInfo.state}
                            onChange={(e) => setShippingInfo(prev => ({ ...prev, state: e.target.value }))}
                            label="State/Province"
                          >
                            {getStateOptions(shippingInfo.country).map((state) => (
                              <MenuItem key={state.value} value={state.value}>
                                {state.label}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          fullWidth
                          label="City"
                          value={shippingInfo.city}
                          onChange={(e) => {
                            setShippingInfo(prev => ({ ...prev, city: e.target.value }));
                            // Clear validation error
                            if (validationErrors.city) {
                              setValidationErrors(prev => {
                                const newErrors = { ...prev };
                                delete newErrors.city;
                                return newErrors;
                              });
                            }
                          }}
                          error={!!validationErrors.city}
                          helperText={validationErrors.city}
                        />
                      </Grid>
                      <Grid size={{ xs: 12, sm: 6 }}>
                        <TextField
                          fullWidth
                          label="Zip/Postal Code"
                          value={shippingInfo.zip}
                          onChange={(e) => {
                            setShippingInfo(prev => ({ ...prev, zip: e.target.value }));
                            // Clear validation error
                            if (validationErrors.zip) {
                              setValidationErrors(prev => {
                                const newErrors = { ...prev };
                                delete newErrors.zip;
                                return newErrors;
                              });
                            }
                          }}
                          error={!!validationErrors.zip}
                          helperText={validationErrors.zip}
                        />
                      </Grid>
                    </Grid>
                  </Box>
                  <Button
                    variant="contained"
                    startIcon={<LocalShippingIcon />}
                    onClick={handleShippingEstimate}
                    disabled={shippingLoading}
                    sx={{ mt: 1, mr: 1 }}
                  >
                    {shippingLoading ? <CircularProgress size={20} /> : 'Estimate Shipping'}
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
              {shippingEstimates.map((option, index) => {
                // Handle the formatted response from backend
                const carrierName = option.carrier_name;
                const methodName = option.method_name;
                const price = option.price;
                const shippingDays = option.shipping_days;
                
                return (
                  <ListItem key={index} divider>
                    <ListItemIcon>
                      <LocalShippingIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={`${carrierName} ${methodName}`}
                      secondary={`${shippingDays} ${shippingDays === 1 ? 'Day' : 'Days'} Shipping`}
                    />
                    <Typography variant="h6" color="primary">
                      {formatPrice(price)}
                    </Typography>
                  </ListItem>
                );
              })}
            </List>
          ) : (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <LocalShippingIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Shipping estimates not available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                We're unable to calculate shipping costs for this item at the moment.
                Please contact us for shipping information.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowShippingDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccessSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSuccessSnackbar(false)}
        message={successMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />

      {/* File Preview Dialog */}
      <Dialog
        open={showPreviewDialog}
        onClose={handleCancelPreview}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Preview & Approve Artwork
            <IconButton onClick={handleCancelPreview}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Review your uploaded files and select which ones to approve for your order.
          </Typography>
          
          <Grid container spacing={2}>
            {previewFiles.map((item, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
                <Card sx={{ height: '100%', position: 'relative' }}>
                  {/* Image preview - commented out for PDF-only restriction */}
                  {/* {item.file.type.startsWith('image/') ? (
                    <CardMedia
                      component="img"
                      height="200"
                      image={item.url}
                      alt={item.file.name}
                      sx={{ objectFit: 'cover' }}
                    />
                  ) : item.file.type === 'application/pdf' ? (
                    <Box sx={{ 
                      height: 400, 
                      overflow: 'auto',
                      bgcolor: 'grey.100'
                    }}>
                      <iframe
                        src={item.url}
                        title={item.file.name}
                        width="100%"
                        height="400px"
                        style={{ border: 'none' }}
                      />
                    </Box>
                  ) : (
                    <Box sx={{ 
                      height: 200, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      bgcolor: 'grey.100'
                    }}>
                      <Typography sx={{ fontSize: 48 }}>
                        {getFileIcon(item.file)}
                      </Typography>
                    </Box>
                  )} */}
                  
                  {/* PDF-only preview */}
                  {item.file.type === 'application/pdf' ? (
                    <Box sx={{ 
                      height: 400, 
                      overflow: 'auto',
                      bgcolor: 'grey.100'
                    }}>
                      <iframe
                        src={item.url}
                        title={item.file.name}
                        width="100%"
                        height="400px"
                        style={{ border: 'none' }}
                      />
                    </Box>
                  ) : (
                    <Box sx={{ 
                      height: 200, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      bgcolor: 'grey.100'
                    }}>
                      <Typography sx={{ fontSize: 48 }}>
                        {getFileIcon(item.file)}
                      </Typography>
                    </Box>
                  )}
                  
                  <CardContent>
                    <Typography variant="subtitle2" noWrap>
                      {item.file.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {formatFileSize(item.file.size)}
                    </Typography>
                    
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={item.approved}
                          onChange={() => handleApproveFile(index)}
                          color="primary"
                        />
                      }
                      label="Approve"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                  
                  {item.approved && (
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        bgcolor: 'success.main',
                        color: 'white',
                        borderRadius: '50%',
                        p: 0.5
                      }}
                    >
                      <CheckCircleIcon fontSize="small" />
                    </Box>
                  )}
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelPreview} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmApproval} 
            variant="contained" 
            startIcon={<CheckCircleIcon />}
            disabled={previewFiles.filter(item => item.approved).length === 0}
          >
            Confirm Approval ({previewFiles.filter(item => item.approved).length})
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProductDetailPage;
