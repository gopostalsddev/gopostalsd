/**
 * Authentication Context for Go Postal SD Frontend
 * 
 * This context provides authentication state and methods throughout the application.
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import authService from '../services/auth_service'

const AuthContext = createContext()

export const useAuth = () => {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Initialize authentication
    useEffect(() => {
        initializeAuth()
    }, [])

    const initializeAuth = async () => {
        try {
            setLoading(true)
            setError(null)

            // Check if user is already authenticated
            if (authService.isAuthenticated()) {
                const currentUser = await authService.getCurrentUser()
                if (currentUser) {
                    // Check if user's email is verified
                    if (!currentUser.email_verified) {
                        // User is not verified, clear auth and don't set user
                        authService.clearAuth()
                    } else {
                        setUser(currentUser)
                    }
                } else {
                    // Token is invalid, clear auth
                    authService.clearAuth()
                }
            }
        } catch (error) {
            console.error('Auth initialization error:', error)
            setError('Failed to initialize authentication')
            authService.clearAuth()
        } finally {
            setLoading(false)
        }
    }

    const login = async (email, password) => {
        try {
            setLoading(true)
            setError(null)

            const response = await authService.login(email, password)
            
            // Check if it's an email verification error
            if (response.success === false && response.code === 'EMAIL_NOT_VERIFIED') {
                return response // Return the error info directly
            }
            
            setUser(response.user)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const register = async (userData) => {
        try {
            setLoading(true)
            setError(null)

            const response = await authService.register(userData)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const logout = async () => {
        try {
            setLoading(true)
            setError(null)

            await authService.logout()
            setUser(null)
            
            return { success: true }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const verifyEmail = async (token) => {
        try {
            setLoading(true)
            setError(null)

            const response = await authService.verifyEmail(token)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const requestPasswordReset = async (email) => {
        try {
            setLoading(true)
            setError(null)

            const response = await authService.requestPasswordReset(email)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const resetPassword = async (token, newPassword) => {
        try {
            setLoading(true)
            setError(null)

            const response = await authService.resetPassword(token, newPassword)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const validatePassword = async (password) => {
        try {
            const response = await authService.validatePassword(password)
            return { success: true, data: response }
        } catch (error) {
            return { success: false, error: error.message }
        }
    }

    const requestEmailVerification = async (email) => {
        try {
            setLoading(true)
            setError(null)
            
            const response = await authService.requestEmailVerification(email)
            
            return { success: true, data: response }
        } catch (error) {
            setError(error.message)
            return { success: false, error: error.message }
        } finally {
            setLoading(false)
        }
    }

    const clearError = () => {
        setError(null)
    }

    const refreshUser = async () => {
        try {
            const currentUser = await authService.getCurrentUser()
            if (currentUser) {
                setUser(currentUser)
                return currentUser
            } else {
                setUser(null)
                return null
            }
        } catch (error) {
            console.error('Error refreshing user:', error)
            setUser(null)
            return null
        }
    }

    const value = {
        // State
        user,
        loading,
        error,
        
        // Computed properties
        isAuthenticated: !!user,
        isEmailVerified: user?.email_verified || false,
        userRole: user?.role || null,
        isAdmin: user?.role === 'Admin',
        isCustomer: user?.role === 'RegisteredCustomer' || user?.role === 'GuestCustomer',
        
        // Methods
        login,
        register,
        logout,
        verifyEmail,
        requestEmailVerification,
        requestPasswordReset,
        resetPassword,
        validatePassword,
        clearError,
        refreshUser
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext
