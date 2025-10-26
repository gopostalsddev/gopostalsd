/**
 * Email Verification Page for Go Postal SD Frontend
 * 
 * This page is shown when a user tries to log in with an unverified email.
 */

import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
    Container,
    Paper,
    Box,
    Typography,
    Button,
    Alert,
    CircularProgress,
    Divider
} from '@mui/material'
import {
    MailOutline,
    CheckCircle,
    Refresh
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const EmailVerificationPage = () => {
    const [email, setEmail] = useState('')
    const [isResending, setIsResending] = useState(false)
    const [resendSuccess, setResendSuccess] = useState(false)
    const [error, setError] = useState('')
    
    const navigate = useNavigate()
    const location = useLocation()
    const { requestEmailVerification } = useAuth()

    useEffect(() => {
        // Get email from location state
        if (location.state?.email) {
            setEmail(location.state.email)
        } else {
            // If no email, redirect to login
            navigate('/login')
        }
    }, [location, navigate])

    const handleResendVerification = async () => {
        setIsResending(true)
        setError('')
        setResendSuccess(false)

        try {
            await requestEmailVerification(email)
            setResendSuccess(true)
        } catch (err) {
            setError(err.message || 'Failed to resend verification email. Please try again.')
        } finally {
            setIsResending(false)
        }
    }

    const handleBackToLogin = () => {
        navigate('/login')
    }

    return (
        <Container maxWidth="sm" sx={{ py: 8 }}>
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
                        Verify Your Email
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        We need to verify your email address to complete your registration
                    </Typography>
                </Box>

                <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <MailOutline sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                        Check Your Email
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        We've sent a verification link to:
                    </Typography>
                    <Typography variant="body1" fontWeight="bold" color="primary.main">
                        {email}
                    </Typography>
                </Box>

                <Divider sx={{ my: 4 }} />

                <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary" paragraph>
                        <strong>What you need to do:</strong>
                    </Typography>
                    <Box component="ol" sx={{ pl: 3, textAlign: 'left' }}>
                        <Box component="li" sx={{ mb: 1 }}>
                            <Typography variant="body2">
                                Check your email inbox for a message from Go Postal SD
                            </Typography>
                        </Box>
                        <Box component="li" sx={{ mb: 1 }}>
                            <Typography variant="body2">
                                Click the verification link in the email
                            </Typography>
                        </Box>
                        <Box component="li" sx={{ mb: 1 }}>
                            <Typography variant="body2">
                                Return to this page or try logging in again
                            </Typography>
                        </Box>
                    </Box>
                </Box>

                <Alert 
                    severity="info" 
                    icon={<MailOutline />}
                    sx={{ mb: 3 }}
                >
                    <Typography variant="body2">
                        <strong>Can't find the email?</strong> Check your spam folder or click the button below to resend.
                    </Typography>
                </Alert>

                {resendSuccess && (
                    <Alert 
                        severity="success" 
                        icon={<CheckCircle />}
                        sx={{ mb: 3 }}
                    >
                        Verification email sent! Please check your inbox.
                    </Alert>
                )}

                {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                        {error}
                    </Alert>
                )}

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Button
                        variant="contained"
                        startIcon={<Refresh />}
                        onClick={handleResendVerification}
                        disabled={isResending}
                        sx={{ mb: 1 }}
                    >
                        {isResending ? (
                            <>
                                <CircularProgress size={20} sx={{ mr: 1 }} />
                                Sending...
                            </>
                        ) : (
                            'Resend Verification Email'
                        )}
                    </Button>
                    
                    <Button
                        variant="outlined"
                        onClick={handleBackToLogin}
                    >
                        Back to Login
                    </Button>
                </Box>

                <Box sx={{ mt: 4, textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                        Need help?{' '}
                        <Button 
                            variant="text" 
                            size="small"
                            onClick={() => navigate('/contact')}
                        >
                            Contact Support
                        </Button>
                    </Typography>
                </Box>
            </Paper>
        </Container>
    )
}

export default EmailVerificationPage
