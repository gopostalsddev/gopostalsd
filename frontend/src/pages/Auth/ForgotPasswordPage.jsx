/**
 * Forgot Password Page for Go Postal SD Frontend
 * 
 * This page handles password reset requests.
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
    Divider,
    Link as MuiLink
} from '@mui/material'
import {
    LockReset,
    Email,
    ArrowBack
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'

const ForgotPasswordPage = () => {
    const [email, setEmail] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [isSubmitted, setIsSubmitted] = useState(false)
    const [error, setError] = useState('')

    const { requestPasswordReset, clearError } = useAuth()
    const navigate = useNavigate()

    // Clear errors when component mounts
    useEffect(() => {
        clearError()
    }, [clearError])

    const handleChange = (e) => {
        setEmail(e.target.value)
        if (error) {
            setError('')
        }
    }

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return emailRegex.test(email)
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        
        if (!email) {
            setError('Email is required')
            return
        }

        if (!validateEmail(email)) {
            setError('Please enter a valid email address')
            return
        }

        setIsSubmitting(true)
        setError('')

        try {
            const result = await requestPasswordReset(email)
            
            if (result.success) {
                setIsSubmitted(true)
            } else {
                setError(result.error || 'Failed to send password reset email')
            }
        } catch (error) {
            setError(error.message || 'Failed to send password reset email')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleBackToLogin = () => {
        navigate('/login')
    }

    const handleTryAgain = () => {
        setIsSubmitted(false)
        setEmail('')
        setError('')
    }

    if (isSubmitted) {
        return (
            <Container maxWidth="sm" sx={{ py: 4 }}>
                <Paper elevation={3} sx={{ p: 4 }}>
                    <Box sx={{ textAlign: 'center' }}>
                        <Email sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
                        <Typography variant="h4" gutterBottom color="success.main">
                            Check Your Email
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                            We've sent a password reset link to <strong>{email}</strong>. 
                            Please check your email and click the link to reset your password.
                        </Typography>
                        
                        <Alert severity="info" sx={{ mb: 4, textAlign: 'left' }}>
                            <Typography variant="body2">
                                <strong>Didn't receive the email?</strong>
                            </Typography>
                            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                                <li>Check your spam/junk folder</li>
                                <li>Make sure you entered the correct email address</li>
                                <li>The email may take a few minutes to arrive</li>
                            </ul>
                        </Alert>
                        
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={handleTryAgain}
                                sx={{ minWidth: 150 }}
                            >
                                Try Again
                            </Button>
                            <Button
                                variant="contained"
                                size="large"
                                onClick={handleBackToLogin}
                                sx={{ minWidth: 150 }}
                            >
                                Back to Login
                            </Button>
                        </Box>
                    </Box>
                </Paper>
            </Container>
        )
    }

    return (
        <Container maxWidth="sm" sx={{ py: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <LockReset sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h4" component="h1" gutterBottom>
                        Forgot Password?
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Enter your email address and we'll send you a link to reset your password.
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
                        type="email"
                        value={email}
                        onChange={handleChange}
                        error={!!error && !email}
                        helperText={error && !email ? error : ''}
                        margin="normal"
                        required
                        InputProps={{
                            startAdornment: (
                                <Email sx={{ mr: 1, color: 'action.active' }} />
                            ),
                        }}
                        disabled={isSubmitting}
                        autoFocus
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={isSubmitting || !email}
                        sx={{ mt: 3, mb: 3 }}
                    >
                        {isSubmitting ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : (
                            'Send Reset Link'
                        )}
                    </Button>
                </Box>

                <Divider sx={{ my: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                        OR
                    </Typography>
                </Divider>

                <Box sx={{ textAlign: 'center' }}>
                    <Button
                        variant="text"
                        startIcon={<ArrowBack />}
                        onClick={handleBackToLogin}
                        sx={{ mb: 2 }}
                    >
                        Back to Login
                    </Button>
                    <br />
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
            </Paper>
        </Container>
    )
}

export default ForgotPasswordPage
