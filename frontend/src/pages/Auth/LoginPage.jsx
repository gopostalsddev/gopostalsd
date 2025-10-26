/**
 * Login Page for Go Postal SD Frontend
 * 
 * This page handles user authentication.
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
    Visibility,
    VisibilityOff,
    Email,
    Lock,
    Login as LoginIcon
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const LoginPage = () => {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    })
    const [showPassword, setShowPassword] = useState(false)
    const [errors, setErrors] = useState({})
    const [isSubmitting, setIsSubmitting] = useState(false)

    const { login, error, clearError, isAuthenticated } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated) {
            const from = location.state?.from?.pathname || '/'
            navigate(from, { replace: true })
        }
    }, [isAuthenticated, navigate, location])

    // Clear errors when component mounts
    useEffect(() => {
        clearError()
    }, [clearError])

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
    }

    const validateForm = () => {
        const newErrors = {}

        if (!formData.email) {
            newErrors.email = 'Email is required'
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid'
        }

        if (!formData.password) {
            newErrors.password = 'Password is required'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (!validateForm()) {
            return
        }

        setIsSubmitting(true)
        clearError()

        try {
            const result = await login(formData.email, formData.password)
            
            if (result.success) {
                const from = location.state?.from?.pathname || '/'
                navigate(from, { replace: true })
            } else if (result.code === 'EMAIL_NOT_VERIFIED') {
                // Redirect to email verification page
                navigate('/verify-email', { 
                    state: { email: formData.email } 
                })
            }
        } catch (error) {
            console.error('Login error:', error)
        } finally {
            setIsSubmitting(false)
        }
    }

    const togglePasswordVisibility = () => {
        setShowPassword(prev => !prev)
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
                        Welcome
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Sign in to your Go Postal SD account
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
                        label="Email Address"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        error={!!errors.email}
                        helperText={errors.email}
                        margin="normal"
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

                    <TextField
                        fullWidth
                        label="Password"
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
                                        onClick={togglePasswordVisibility}
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

                    <Box sx={{ textAlign: 'right', mt: 1, mb: 3 }}>
                        <MuiLink
                            component={Link}
                            to="/forgot-password"
                            variant="body2"
                            color="primary"
                        >
                            Forgot your password?
                        </MuiLink>
                    </Box>

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={isSubmitting}
                        sx={{ mb: 3 }}
                    >
                        {isSubmitting ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : (
                            'Sign In'
                        )}
                    </Button>

                    <Divider sx={{ my: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                            OR
                        </Typography>
                    </Divider>

                    <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="body2" color="text.secondary">
                            Don't have an account?{' '}
                            <MuiLink
                                component={Link}
                                to="/register"
                                variant="body2"
                                color="primary"
                            >
                                Sign up here
                            </MuiLink>
                        </Typography>
                    </Box>
                </Box>
            </Paper>
        </Container>
    )
}

export default LoginPage
