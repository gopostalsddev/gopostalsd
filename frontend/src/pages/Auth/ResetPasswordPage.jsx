/**
 * Reset Password Page for Go Postal SD Frontend
 * 
 * This page handles password reset with token.
 */

import React, { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
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
    Link as MuiLink
} from '@mui/material'
import {
    Lock,
    Visibility,
    VisibilityOff,
    CheckCircle,
    Error
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const ResetPasswordPage = () => {
    const [formData, setFormData] = useState({
        password: '',
        confirmPassword: ''
    })
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [errors, setErrors] = useState({})
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)
    const [error, setError] = useState('')
    const [passwordValidation, setPasswordValidation] = useState(null)

    const { resetPassword, validatePassword, clearError } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()

    // Get token from URL parameters
    const searchParams = new URLSearchParams(location.search)
    const token = searchParams.get('token')

    useEffect(() => {
        if (!token) {
            setError('Invalid or missing reset token')
        }
        clearError()
    }, [token, clearError])

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
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
        
        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }))
        }
        
        if (error) {
            setError('')
        }
    }

    const validateForm = () => {
        const newErrors = {}

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

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (!token) {
            setError('Invalid or missing reset token')
            return
        }

        if (!validateForm()) {
            return
        }

        setIsSubmitting(true)
        setError('')

        try {
            const result = await resetPassword(token, formData.password)
            
            if (result.success) {
                setIsSuccess(true)
            } else {
                setError(result.error || 'Password reset failed')
            }
        } catch (error) {
            setError(error.message || 'Password reset failed')
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

    const handleGoToLogin = () => {
        navigate('/login')
    }

    if (isSuccess) {
        return (
            <Container maxWidth="sm" sx={{ py: 4 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Box sx={{ textAlign: 'center' }}>
                        <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
                        <Typography variant="h4" gutterBottom color="success.main">
                            Password Reset Successful!
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                            Your password has been successfully reset. You can now sign in with your new password.
                        </Typography>
                        
                        <Button
                            variant="contained"
                            size="large"
                            onClick={handleGoToLogin}
                            sx={{ minWidth: 200 }}
                        >
                            Sign In Now
                        </Button>
                    </Box>
                </Paper>
            </Container>
        )
    }

    if (!token) {
        return (
            <Container maxWidth="sm" sx={{ py: 4 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Box sx={{ textAlign: 'center' }}>
                        <Error sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
                        <Typography variant="h4" gutterBottom color="error.main">
                            Invalid Reset Link
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                            This password reset link is invalid or has expired. Please request a new one.
                        </Typography>
                        
                        <Button
                            variant="contained"
                            size="large"
                            component={Link}
                            to="/forgot-password"
                            sx={{ minWidth: 200 }}
                        >
                            Request New Reset Link
                        </Button>
                    </Box>
                </Paper>
            </Container>
        )
    }

    return (
        <Container maxWidth="sm" sx={{ py: 4 }}>
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
                        Reset Your Password
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Enter your new password below.
                    </Typography>
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit}>
                    <TextField
                        fullWidth
                        label="New Password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleChange}
                        error={!!errors.password}
                        helperText={errors.password}
                        margin="normal"
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
                        autoFocus
                    />
                    
                    {passwordValidation && (
                        <Box sx={{ mt: 1, mb: 2 }}>
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

                    <TextField
                        fullWidth
                        label="Confirm New Password"
                        name="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        error={!!errors.confirmPassword}
                        helperText={errors.confirmPassword}
                        margin="normal"
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

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={isSubmitting}
                        sx={{ mt: 3, mb: 3 }}
                    >
                        {isSubmitting ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : (
                            'Reset Password'
                        )}
                    </Button>
                </Box>

                <Divider sx={{ my: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        OR
                    </Typography>
                </Divider>

                <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Remember your password?{' '}
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

export default ResetPasswordPage
