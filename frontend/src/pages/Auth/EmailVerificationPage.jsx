/**
 * Email Verification Page for Go Postal SD Frontend
 * 
 * This page handles email verification after user registration.
 */

import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import {
    Container,
    Paper,
    Box,
    Typography,
    Button,
    Alert,
    CircularProgress,
    Divider,
    Link as MuiLink
} from '@mui/material'
import {
    Email,
    CheckCircle,
    Error,
    Refresh
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'

const EmailVerificationPage = () => {
    const [verificationStatus, setVerificationStatus] = useState('verifying') // 'verifying', 'success', 'error'
    const [error, setError] = useState('')
    const [isVerifying, setIsVerifying] = useState(false)

    const { verifyEmail, clearError } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()

    // Get token from URL parameters
    const searchParams = new URLSearchParams(location.search)
    const token = searchParams.get('token')
    const email = location.state?.email

    useEffect(() => {
        if (token) {
            handleVerification(token)
        } else {
            setVerificationStatus('error')
            setError('No verification token provided')
        }
    }, [token])

    const handleVerification = async (verificationToken) => {
        try {
            setIsVerifying(true)
            setError('')
            clearError()

            const result = await verifyEmail(verificationToken)
            
            if (result.success) {
                setVerificationStatus('success')
            } else {
                setVerificationStatus('error')
                setError(result.error || 'Email verification failed')
            }
        } catch (error) {
            setVerificationStatus('error')
            setError(error.message || 'Email verification failed')
        } finally {
            setIsVerifying(false)
        }
    }

    const handleResendVerification = () => {
        // This would typically redirect to a resend verification page
        navigate('/resend-verification', { state: { email } })
    }

    const handleGoToLogin = () => {
        navigate('/login')
    }

    const handleGoToHome = () => {
        navigate('/')
    }

    const renderContent = () => {
        switch (verificationStatus) {
            case 'verifying':
                return (
                    <Box sx={{ textAlign: 'center' }}>
                        <CircularProgress size={60} sx={{ mb: 3 }} />
                        <Typography variant="h5" gutterBottom>
                            Verifying Your Email
                        </Typography>
                        <Typography variant="body1" color="text.secondary">
                            Please wait while we verify your email address...
                        </Typography>
                    </Box>
                )

            case 'success':
                return (
                    <Box sx={{ textAlign: 'center' }}>
                        <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 3 }} />
                        <Typography variant="h4" gutterBottom color="success.main">
                            Email Verified Successfully!
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                            Your email address has been verified. You can now access all features of Go Postal SD.
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Button
                                variant="contained"
                                size="large"
                                onClick={handleGoToLogin}
                                sx={{ minWidth: 150 }}
                            >
                                Sign In
                            </Button>
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={handleGoToHome}
                                sx={{ minWidth: 150 }}
                            >
                                Go to Home
                            </Button>
                        </Box>
                    </Box>
                )

            case 'error':
                return (
                    <Box sx={{ textAlign: 'center' }}>
                        <Error sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
                        <Typography variant="h4" gutterBottom color="error.main">
                            Verification Failed
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                            {error || 'There was an error verifying your email address.'}
                        </Typography>
                        
                        <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
                            <Typography variant="body2">
                                <strong>Possible reasons:</strong>
                            </Typography>
                            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                                <li>The verification link has expired</li>
                                <li>The verification link has already been used</li>
                                <li>The verification link is invalid</li>
                            </ul>
                        </Alert>
                        
                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Button
                                variant="contained"
                                size="large"
                                startIcon={<Refresh />}
                                onClick={handleResendVerification}
                                sx={{ minWidth: 200 }}
                            >
                                Resend Verification
                            </Button>
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={handleGoToLogin}
                                sx={{ minWidth: 150 }}
                            >
                                Back to Login
                            </Button>
                        </Box>
                    </Box>
                )

            default:
                return null
        }
    }

    return (
        <Container maxWidth="sm" sx={{ py: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <Email sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h4" component="h1" gutterBottom>
                        Email Verification
                    </Typography>
                    {email && (
                        <Typography variant="body2" color="text.secondary">
                            Verifying email: {email}
                        </Typography>
                    )}
                </Box>

                {renderContent()}

                <Divider sx={{ my: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                        Need Help?
                    </Typography>
                </Divider>

                <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        If you're having trouble verifying your email, please contact our support team.
                    </Typography>
                    <MuiLink
                        component={Link}
                        to="/contact"
                        variant="body2"
                        color="primary"
                    >
                        Contact Support
                    </MuiLink>
                </Box>
            </Paper>
        </Container>
    )
}

export default EmailVerificationPage
