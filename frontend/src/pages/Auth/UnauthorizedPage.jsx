/**
 * Unauthorized Access Page for Go Postal SD Frontend
 * 
 * This page is displayed when users try to access resources they don't have permission for.
 */

import React from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import {
    Container,
    Paper,
    Box,
    Typography,
    Button,
    Alert,
    Divider,
    Link as MuiLink
} from '@mui/material'
import {
    Block,
    Home,
    Login,
    ArrowBack
} from '@mui/icons-material'
import { useAuth } from '../../contexts/AuthContext'
import logo from '../../assets/logo.png'

const UnauthorizedPage = () => {
    const { isAuthenticated, userRole } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()

    const from = location.state?.from?.pathname || '/'

    const handleGoBack = () => {
        if (from && from !== '/unauthorized') {
            navigate(from)
        } else {
            navigate('/')
        }
    }

    const handleGoHome = () => {
        navigate('/')
    }

    const handleGoToLogin = () => {
        navigate('/login', { state: { from: location } })
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
                    <Block sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
                    <Typography variant="h3" component="h1" gutterBottom color="error.main">
                        Access Denied
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                        403 - Unauthorized Access
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        You don't have permission to access this resource.
                    </Typography>
                </Box>

                <Alert severity="warning" sx={{ mb: 4 }}>
                    <Typography variant="body2">
                        <strong>What does this mean?</strong>
                    </Typography>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                        <li>You may not be logged in</li>
                        <li>Your account may not have the required permissions</li>
                        <li>The resource may require a different role or access level</li>
                        <li>The page you're trying to access may not exist</li>
                    </ul>
                </Alert>

                {isAuthenticated ? (
                    <Box sx={{ mb: 4 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            <strong>Current Status:</strong> Logged in as {userRole}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            If you believe you should have access to this resource, please contact your administrator.
                        </Typography>
                    </Box>
                ) : (
                    <Box sx={{ mb: 4 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                            <strong>Current Status:</strong> Not logged in
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            You may need to sign in to access this resource.
                        </Typography>
                    </Box>
                )}

                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap', mb: 4 }}>
                    <Button
                        variant="contained"
                        size="large"
                        startIcon={<ArrowBack />}
                        onClick={handleGoBack}
                        sx={{ minWidth: 150 }}
                    >
                        Go Back
                    </Button>
                    
                    <Button
                        variant="outlined"
                        size="large"
                        startIcon={<Home />}
                        onClick={handleGoHome}
                        sx={{ minWidth: 150 }}
                    >
                        Go Home
                    </Button>
                    
                    {!isAuthenticated && (
                        <Button
                            variant="contained"
                            size="large"
                            startIcon={<Login />}
                            onClick={handleGoToLogin}
                            sx={{ minWidth: 150 }}
                        >
                            Sign In
                        </Button>
                    )}
                </Box>

                <Divider sx={{ my: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                        Need Help?
                    </Typography>
                </Divider>

                <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        If you continue to experience issues, please contact our support team.
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                        <MuiLink
                            component={Link}
                            to="/contact"
                            variant="body2"
                            color="primary"
                        >
                            Contact Support
                        </MuiLink>
                        <Typography variant="body2" color="text.secondary">
                            •
                        </Typography>
                        <MuiLink
                            component={Link}
                            to="/faqs"
                            variant="body2"
                            color="primary"
                        >
                            FAQ
                        </MuiLink>
                    </Box>
                </Box>
            </Paper>
        </Container>
    )
}

export default UnauthorizedPage
