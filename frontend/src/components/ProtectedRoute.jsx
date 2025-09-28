/**
 * Protected Route Component for Go Postal SD Frontend
 * 
 * This component protects routes that require authentication.
 */

import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Box, CircularProgress, Typography } from '@mui/material'

const ProtectedRoute = ({ 
    children, 
    requireAuth = true, 
    requireEmailVerification = false,
    requireRole = null,
    requirePermission = null,
    redirectTo = '/login'
}) => {
    const { user, loading, isAuthenticated, isEmailVerified } = useAuth()
    const location = useLocation()

    // Show loading spinner while checking authentication
    if (loading) {
        return (
            <Box 
                display="flex" 
                flexDirection="column" 
                alignItems="center" 
                justifyContent="center" 
                minHeight="50vh"
                gap={2}
            >
                <CircularProgress size={40} />
                <Typography variant="body2" color="text.secondary">
                    Loading...
                </Typography>
            </Box>
        )
    }

    // Check authentication requirement
    if (requireAuth && !isAuthenticated) {
        return <Navigate to={redirectTo} state={{ from: location }} replace />
    }

    // Check email verification requirement
    if (requireEmailVerification && !isEmailVerified) {
        return <Navigate to="/verify-email" state={{ from: location }} replace />
    }

    // Check role requirement
    if (requireRole && user?.role !== requireRole) {
        return <Navigate to="/unauthorized" state={{ from: location }} replace />
    }

    // Check permission requirement
    if (requirePermission) {
        // This would need to be implemented based on your permission system
        // For now, we'll just check if user has admin role for admin permissions
        const hasPermission = user?.role === 'Admin' || 
                            (requirePermission.startsWith('customer.') && user?.role === 'RegisteredCustomer')
        
        if (!hasPermission) {
            return <Navigate to="/unauthorized" state={{ from: location }} replace />
        }
    }

    return children
}

export default ProtectedRoute
