/**
 * Verify Email Page for Go Postal SD Frontend
 * 
 * This page handles email verification from the verification link.
 */

import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
    Container,
    Paper,
    Box,
    Typography,
    Button,
    Alert,
    CircularProgress
} from '@mui/material'
import {
    CheckCircle,
    Error,
    Email
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const VerifyEmailPage = () => {
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const { verifyEmail } = useAuth()
    
    const [status, setStatus] = useState('verifying') // verifying, success, error
    const [message, setMessage] = useState('')
    const [error, setError] = useState('')

    useEffect(() => {
        const token = searchParams.get('token')
        
        if (!token) {
            setStatus('error')
            setError('No verification token provided')
            return
        }

        const verify = async () => {
            try {
                const result = await verifyEmail(token)
                
                if (result.success) {
                    setStatus('success')
                    setMessage(result.data?.message || 'Your email has been verified successfully! You can now log in.')
                } else {
                    setStatus('error')
                    setError(result.error || 'Verification failed')
                }
            } catch (err) {
                console.error('Verification error:', err)
                setStatus('error')
                setError(err.message || 'Verification failed')
            }
        }

        verify()
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []) // Only run once on mount

    const handleGoToLogin = () => {
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
                </Box>

                {status === 'verifying' && (
                    <Box sx={{ textAlign: 'center' }}>
                        <CircularProgress sx={{ mb: 3 }} />
                        <Typography variant="h6" gutterBottom>
                            Verifying Your Email
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Please wait while we verify your email address...
                        </Typography>
                    </Box>
                )}

                {status === 'success' && (
                    <>
                        <Box sx={{ textAlign: 'center', mb: 4 }}>
                            <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                            <Typography variant="h5" gutterBottom color="success.main">
                                Email Verified!
                            </Typography>
                        </Box>

                        <Alert 
                            severity="success" 
                            icon={<CheckCircle />}
                            sx={{ mb: 3 }}
                        >
                            {message}
                        </Alert>

                        <Button
                            variant="contained"
                            fullWidth
                            onClick={handleGoToLogin}
                            sx={{ mt: 2 }}
                        >
                            Go to Login
                        </Button>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <Box sx={{ textAlign: 'center', mb: 4 }}>
                            <Error sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
                            <Typography variant="h5" gutterBottom color="error.main">
                                Verification Failed
                            </Typography>
                        </Box>

                        <Alert 
                            severity="error"
                            icon={<Error />}
                            sx={{ mb: 3 }}
                        >
                            {error}
                        </Alert>

                        <Box sx={{ display: 'flex', gap: 2 }}>
                            <Button
                                variant="contained"
                                fullWidth
                                onClick={handleGoToLogin}
                            >
                                Go to Login
                            </Button>
                            <Button
                                variant="outlined"
                                fullWidth
                                onClick={() => navigate('/verify-email')}
                            >
                                Try Again
                            </Button>
                        </Box>
                    </>
                )}
            </Paper>
        </Container>
    )
}

export default VerifyEmailPage

