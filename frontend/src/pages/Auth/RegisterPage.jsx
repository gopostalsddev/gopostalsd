/**
 * Registration Page for Go Postal SD Frontend
 * 
 * This page handles user registration.
 */

import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
    Container,
    Paper,
    Box,
    TextField,
    Button,
    Typography,
    Alert,
    CircularProgress,
    InputAdornment,
    IconButton,
    Divider,
    Link as MuiLink,
    Grid,
    Stepper,
    Step,
    StepLabel
} from '@mui/material'
import {
    Visibility,
    VisibilityOff,
    Email,
    Lock,
    Person,
    Home,
    LocationOn,
    PersonAdd
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const steps = ['Account Information', 'Address Information', 'Review & Submit']

const RegisterPage = () => {
    const [activeStep, setActiveStep] = useState(0)
    const [formData, setFormData] = useState({
        // Account information
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        
        // Address information
        shipping_address: {
            street: '',
            city: '',
            state: '',
            zip_code: '',
            country: 'US',
            apt: ''
        },
        billing_address: {
            street: '',
            city: '',
            state: '',
            zip_code: '',
            country: 'US',
            apt: ''
        },
        use_same_address: true
    })
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [errors, setErrors] = useState({})
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [passwordValidation, setPasswordValidation] = useState(null)

    const { register, error, clearError, validatePassword } = useAuth()
    const navigate = useNavigate()

    // Clear errors when component mounts
    useEffect(() => {
        clearError()
    }, [clearError])

    // Validate password strength
    useEffect(() => {
        if (formData.password) {
            validatePassword(formData.password).then(result => {
                if (result.success) {
                    setPasswordValidation(result.data)
                }
            })
        } else {
            setPasswordValidation(null)
        }
    }, [formData.password, validatePassword])

    const handleChange = (e) => {
        const { name, value } = e.target
        
        if (name.startsWith('shipping_') || name.startsWith('billing_')) {
            const addressType = name.startsWith('shipping_') ? 'shipping' : 'billing'
            const field = name.substring(addressType.length + 1) // Remove 'shipping_' or 'billing_' prefix
            setFormData(prev => ({
                ...prev,
                [`${addressType}_address`]: {
                    ...prev[`${addressType}_address`],
                    [field]: value
                }
            }))
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }))
        }
        
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }))
        }
    }

    const handleCheckboxChange = (e) => {
        const { name, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: checked
        }))
        
        // If using same address, copy shipping to billing
        if (name === 'use_same_address' && checked) {
            setFormData(prev => ({
                ...prev,
                billing_address: prev.shipping_address
            }))
        }
    }

    const validateStep = (step) => {
        const newErrors = {}

        if (step === 0) {
            // Account information validation
            if (!formData.email) {
                newErrors.email = 'Email is required'
            } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
                newErrors.email = 'Email is invalid'
            }

            if (!formData.password) {
                newErrors.password = 'Password is required'
            } else if (passwordValidation && !passwordValidation.is_valid) {
                newErrors.password = 'Password does not meet requirements'
            }

            if (!formData.confirmPassword) {
                newErrors.confirmPassword = 'Please confirm your password'
            } else if (formData.password !== formData.confirmPassword) {
                newErrors.confirmPassword = 'Passwords do not match'
            }

            if (!formData.first_name) {
                newErrors.first_name = 'First name is required'
            }

            if (!formData.last_name) {
                newErrors.last_name = 'Last name is required'
            }
        } else if (step === 1) {
            // Address information validation
            const addressFields = ['street', 'city', 'state', 'zip_code', 'country']
            
            addressFields.forEach(field => {
                if (!formData.shipping_address[field]) {
                    newErrors[`shipping_${field}`] = `${field.charAt(0).toUpperCase() + field.slice(1)} is required`
                }
            })

            if (!formData.use_same_address) {
                addressFields.forEach(field => {
                    if (!formData.billing_address[field]) {
                        newErrors[`billing_${field}`] = `${field.charAt(0).toUpperCase() + field.slice(1)} is required`
                    }
                })
            }
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleNext = () => {
        if (validateStep(activeStep)) {
            setActiveStep(prev => prev + 1)
        }
    }

    const handleBack = () => {
        setActiveStep(prev => prev - 1)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (!validateStep(activeStep)) {
            return
        }

        setIsSubmitting(true)
        clearError()

        try {
            const registrationData = {
                email: formData.email,
                password: formData.password,
                first_name: formData.first_name,
                last_name: formData.last_name,
                shipping_address: formData.shipping_address,
                billing_address: formData.use_same_address ? undefined : formData.billing_address
            }

            const result = await register(registrationData)
            
            if (result.success) {
                navigate('/verify-email', { 
                    state: { email: formData.email } 
                })
            } else {
                // Handle specific error cases
                if (result.error && result.error.code === 'USER_EXISTS') {
                    // Clear the email field and show specific error
                    setFormData(prev => ({ ...prev, email: '' }))
                    setErrors(prev => ({ ...prev, email: 'An account with this email already exists' }))
                }
            }
        } catch (error) {
            console.error('Registration error:', error)
            // Error is already handled by AuthContext and displayed via the error state
        } finally {
            setIsSubmitting(false)
        }
    }

    const togglePasswordVisibility = (field) => {
        if (field === 'password') {
            setShowPassword(prev => !prev)
        } else {
            setShowConfirmPassword(prev => !prev)
        }
    }

    const renderStepContent = (step) => {
        switch (step) {
            case 0:
                return (
                    <Box>
                        <Grid container spacing={2}>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField
                                    fullWidth
                                    label="First Name"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    error={!!errors.first_name}
                                    helperText={errors.first_name}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField
                                    fullWidth
                                    label="Last Name"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    error={!!errors.last_name}
                                    helperText={errors.last_name}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <TextField
                                    fullWidth
                                    label="Email Address"
                                    name="email"
                                    type="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    error={!!errors.email}
                                    helperText={errors.email}
                                    required
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <Email color="action" />
                                            </InputAdornment>
                                        ),
                                    }}
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <TextField
                                    fullWidth
                                    label="Password"
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={formData.password}
                                    onChange={handleChange}
                                    error={!!errors.password}
                                    helperText={errors.password}
                                    required
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <Lock color="action" />
                                            </InputAdornment>
                                        ),
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('password')}
                                                    edge="end"
                                                    disabled={isSubmitting}
                                                >
                                                    {showPassword ? <VisibilityOff /> : <Visibility />}
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                    disabled={isSubmitting}
                                />
                                {passwordValidation && (
                                    <Box sx={{ mt: 1 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            Strength: {passwordValidation.strength_level} ({passwordValidation.strength_score}/100)
                                        </Typography>
                                        {passwordValidation.errors.length > 0 && (
                                            <Box>
                                                {passwordValidation.errors.map((error, index) => (
                                                    <Typography key={index} variant="caption" color="error" display="block">
                                                        • {error}
                                                    </Typography>
                                                ))}
                                            </Box>
                                        )}
                                    </Box>
                                )}
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <TextField
                                    fullWidth
                                    label="Confirm Password"
                                    name="confirmPassword"
                                    type={showConfirmPassword ? 'text' : 'password'}
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    error={!!errors.confirmPassword}
                                    helperText={errors.confirmPassword}
                                    required
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <Lock color="action" />
                                            </InputAdornment>
                                        ),
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    onClick={() => togglePasswordVisibility('confirmPassword')}
                                                    edge="end"
                                                    disabled={isSubmitting}
                                                >
                                                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                    disabled={isSubmitting}
                                />
                            </Grid>
                        </Grid>
                    </Box>
                )

            case 1:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Shipping Address
                        </Typography>
                        <Grid container spacing={2} sx={{ mb: 3 }}>
                            <Grid size={{ xs: 12 }}>
                                <TextField
                                    fullWidth
                                    label="Street Address"
                                    name="shipping_street"
                                    value={formData.shipping_address.street}
                                    onChange={handleChange}
                                    error={!!errors.shipping_street}
                                    helperText={errors.shipping_street}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 8 }}>
                                <TextField
                                    fullWidth
                                    label="City"
                                    name="shipping_city"
                                    value={formData.shipping_address.city}
                                    onChange={handleChange}
                                    error={!!errors.shipping_city}
                                    helperText={errors.shipping_city}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 4 }}>
                                <TextField
                                    fullWidth
                                    label="ZIP Code"
                                    name="shipping_zip_code"
                                    value={formData.shipping_address.zip_code}
                                    onChange={handleChange}
                                    error={!!errors.shipping_zip_code}
                                    helperText={errors.shipping_zip_code}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField
                                    fullWidth
                                    label="State"
                                    name="shipping_state"
                                    value={formData.shipping_address.state}
                                    onChange={handleChange}
                                    error={!!errors.shipping_state}
                                    helperText={errors.shipping_state}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12, sm: 6 }}>
                                <TextField
                                    fullWidth
                                    label="Country"
                                    name="shipping_country"
                                    value={formData.shipping_address.country}
                                    onChange={handleChange}
                                    error={!!errors.shipping_country}
                                    helperText={errors.shipping_country}
                                    required
                                    disabled={isSubmitting}
                                />
                            </Grid>
                            <Grid size={{ xs: 12 }}>
                                <TextField
                                    fullWidth
                                    label="Apartment/Suite (Optional)"
                                    name="shipping_apt"
                                    value={formData.shipping_address.apt}
                                    onChange={handleChange}
                                    disabled={isSubmitting}
                                />
                            </Grid>
                        </Grid>

                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <input
                                type="checkbox"
                                id="use_same_address"
                                name="use_same_address"
                                checked={formData.use_same_address}
                                onChange={handleCheckboxChange}
                                disabled={isSubmitting}
                            />
                            <label htmlFor="use_same_address" style={{ marginLeft: 8 }}>
                                Use same address for billing
                            </label>
                        </Box>

                        {!formData.use_same_address && (
                            <>
                                <Typography variant="h6" gutterBottom>
                                    Billing Address
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid size={{ xs: 12 }}>
                                        <TextField
                                            fullWidth
                                            label="Street Address"
                                            name="billing_street"
                                            value={formData.billing_address.street}
                                            onChange={handleChange}
                                            error={!!errors.billing_street}
                                            helperText={errors.billing_street}
                                            required
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                    <Grid size={{ xs: 12, sm: 8 }}>
                                        <TextField
                                            fullWidth
                                            label="City"
                                            name="billing_city"
                                            value={formData.billing_address.city}
                                            onChange={handleChange}
                                            error={!!errors.billing_city}
                                            helperText={errors.billing_city}
                                            required
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                    <Grid size={{ xs: 12, sm: 4 }}>
                                        <TextField
                                            fullWidth
                                            label="ZIP Code"
                                            name="billing_zip_code"
                                            value={formData.billing_address.zip_code}
                                            onChange={handleChange}
                                            error={!!errors.billing_zip_code}
                                            helperText={errors.billing_zip_code}
                                            required
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                    <Grid size={{ xs: 12, sm: 6 }}>
                                        <TextField
                                            fullWidth
                                            label="State"
                                            name="billing_state"
                                            value={formData.billing_address.state}
                                            onChange={handleChange}
                                            error={!!errors.billing_state}
                                            helperText={errors.billing_state}
                                            required
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                    <Grid size={{ xs: 12, sm: 6 }}>
                                        <TextField
                                            fullWidth
                                            label="Country"
                                            name="billing_country"
                                            value={formData.billing_address.country}
                                            onChange={handleChange}
                                            error={!!errors.billing_country}
                                            helperText={errors.billing_country}
                                            required
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                    <Grid size={{ xs: 12 }}>
                                        <TextField
                                            fullWidth
                                            label="Apartment/Suite (Optional)"
                                            name="billing_apt"
                                            value={formData.billing_address.apt}
                                            onChange={handleChange}
                                            disabled={isSubmitting}
                                        />
                                    </Grid>
                                </Grid>
                            </>
                        )}
                    </Box>
                )

            case 2:
                return (
                    <Box>
                        <Typography variant="h6" gutterBottom>
                            Review Your Information
                        </Typography>
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" gutterBottom>
                                Account Information
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Name: {formData.first_name} {formData.last_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Email: {formData.email}
                            </Typography>
                        </Box>
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="subtitle1" gutterBottom>
                                Shipping Address
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {formData.shipping_address.street}
                                {formData.shipping_address.apt && `, ${formData.shipping_address.apt}`}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {formData.shipping_address.city}, {formData.shipping_address.state} {formData.shipping_address.zip_code}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                {formData.shipping_address.country}
                            </Typography>
                        </Box>
                        {!formData.use_same_address && (
                            <Box sx={{ mb: 3 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                    Billing Address
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {formData.billing_address.street}
                                    {formData.billing_address.apt && `, ${formData.billing_address.apt}`}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {formData.billing_address.city}, {formData.billing_address.state} {formData.billing_address.zip_code}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {formData.billing_address.country}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                )

            default:
                return null
        }
    }

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <Box sx={{ mb: 3 }}>
                        <img 
                            src={logo} 
                            alt="Go Postal SD Logo" 
                            style={{ height: '80px', width: 'auto' }}
                        />
                    </Box>
                    <Typography variant="h4" component="h1" gutterBottom color="primary">
                        Create Account
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Join Go Postal SD and start your printing journey
                    </Typography>
                </Box>

                <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                        {error.includes('email already exists') && (
                            <Box sx={{ mt: 1 }}>
                                <MuiLink 
                                    component={Link} 
                                    to="/login"
                                    sx={{ textDecoration: 'underline' }}
                                >
                                    Click here to log in instead
                                </MuiLink>
                            </Box>
                        )}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit}>
                    {renderStepContent(activeStep)}

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                        <Button
                            disabled={activeStep === 0 || isSubmitting}
                            onClick={handleBack}
                        >
                            Back
                        </Button>
                        
                        {activeStep === steps.length - 1 ? (
                            <Button
                                type="submit"
                                variant="contained"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? (
                                    <CircularProgress size={24} color="inherit" />
                                ) : (
                                    'Create Account'
                                )}
                            </Button>
                        ) : (
                            <Button
                                variant="contained"
                                onClick={handleNext}
                                disabled={isSubmitting}
                            >
                                Next
                            </Button>
                        )}
                    </Box>
                </Box>

                <Divider sx={{ my: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        OR
                    </Typography>
                </Divider>

                <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Already have an account?{' '}
                        <MuiLink
                            component={Link}
                            to="/login"
                            variant="body2"
                            color="primary"
                        >
                            Sign in here
                        </MuiLink>
                    </Typography>
                </Box>
            </Paper>
        </Container>
    )
}

export default RegisterPage
