/**
 * Authentication Service for Go Postal SD Frontend
 * 
 * This service handles all authentication-related API calls and token management.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

class AuthService {
    constructor() {
        this.tokenKey = 'gopostalsd_session_token'
        this.refreshTokenKey = 'gopostalsd_refresh_token'
        this.userKey = 'gopostalsd_user'
    }

    // Token management
    getToken() {
        return localStorage.getItem(this.tokenKey)
    }

    setToken(token) {
        localStorage.setItem(this.tokenKey, token)
    }

    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey)
    }

    setRefreshToken(refreshToken) {
        localStorage.setItem(this.refreshTokenKey, refreshToken)
    }

    getUser() {
        const userStr = localStorage.getItem(this.userKey)
        return userStr ? JSON.parse(userStr) : null
    }

    setUser(user) {
        localStorage.setItem(this.userKey, JSON.stringify(user))
    }

    clearAuth() {
        localStorage.removeItem(this.tokenKey)
        localStorage.removeItem(this.refreshTokenKey)
        localStorage.removeItem(this.userKey)
    }

    // Authentication methods
    async register(userData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/register`, userData)
            return response.data
        } catch (error) {
            console.error('Registration error:', error)
            throw this.handleError(error)
        }
    }

    async verifyEmail(token) {
        try {
            const response = await axios.get(`${API_BASE_URL}/auth/verify-email?token=${token}`)
            return response.data
        } catch (error) {
            console.error('Email verification error:', error)
            throw this.handleError(error)
        }
    }

    async requestEmailVerification(email) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/resend-verification`, { email })
            return response.data
        } catch (error) {
            console.error('Resend verification error:', error)
            throw this.handleError(error)
        }
    }

    async login(email, password) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/login`, {
                email,
                password
            })
            
            const { user, session } = response.data
            
            // Store authentication data
            this.setToken(session.session_token)
            this.setRefreshToken(session.refresh_token)
            this.setUser(user)
            
            return response.data
        } catch (error) {
            // Check if it's an email verification error
            if (error.response?.data?.code === 'EMAIL_NOT_VERIFIED') {
                // Return the error data so LoginPage can handle it
                return {
                    success: false,
                    code: 'EMAIL_NOT_VERIFIED',
                    email: error.response.data.email,
                    user_id: error.response.data.user_id,
                    requires_verification: true
                }
            }
            throw this.handleError(error)
        }
    }

    async logout() {
        try {
            const token = this.getToken()
            if (token) {
                await axios.post(`${API_BASE_URL}/auth/logout?session_token=${token}`)
            }
        } catch (error) {
            console.error('Logout error:', error)
        } finally {
            // Clear local storage regardless of API call success
            this.clearAuth()
        }
    }

    async refreshSession() {
        try {
            const refreshToken = this.getRefreshToken()
            if (!refreshToken) {
                throw new Error('No refresh token available')
            }

            const response = await axios.post(`${API_BASE_URL}/auth/refresh?refresh_token=${refreshToken}`)
            const { session } = response.data
            
            // Update stored tokens
            this.setToken(session.session_token)
            this.setRefreshToken(session.refresh_token)
            
            return response.data
        } catch (error) {
            console.error('Session refresh error:', error)
            // If refresh fails, clear auth and redirect to login
            this.clearAuth()
            throw this.handleError(error)
        }
    }

    async requestPasswordReset(email) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/password-reset/request`, {
                email
            })
            return response.data
        } catch (error) {
            console.error('Password reset request error:', error)
            throw this.handleError(error)
        }
    }

    async resetPassword(token, newPassword) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/password-reset`, {
                token,
                new_password: newPassword
            })
            return response.data
        } catch (error) {
            console.error('Password reset error:', error)
            throw this.handleError(error)
        }
    }

    async getCurrentUser() {
        try {
            const token = this.getToken()
            if (!token) {
                return null
            }

            const response = await axios.get(`${API_BASE_URL}/auth/me?session_token=${token}`)
            return response.data
        } catch (error) {
            console.error('Get current user error:', error)
            // If getting current user fails, clear auth
            this.clearAuth()
            return null
        }
    }

    async validatePassword(password) {
        try {
            const response = await axios.post(`${API_BASE_URL}/auth/validate-password`, {
                password
            })
            return response.data
        } catch (error) {
            console.error('Password validation error:', error)
            throw this.handleError(error)
        }
    }

    // Utility methods
    isAuthenticated() {
        return !!this.getToken()
    }

    isEmailVerified() {
        const user = this.getUser()
        return user ? user.email_verified : false
    }

    getUserRole() {
        const user = this.getUser()
        return user ? user.role : null
    }

    isAdmin() {
        return this.getUserRole() === 'Admin'
    }

    isCustomer() {
        const role = this.getUserRole()
        return role === 'RegisteredCustomer' || role === 'GuestCustomer'
    }

    // Axios interceptor setup
    setupAxiosInterceptors() {
        // Request interceptor to add auth token
        axios.interceptors.request.use(
            (config) => {
                const token = this.getToken()
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`
                }
                return config
            },
            (error) => {
                return Promise.reject(error)
            }
        )

        // Response interceptor to handle token refresh
        axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                const originalRequest = error.config

                // Don't try to refresh if it's an email verification error
                if (error.response?.data?.code === 'EMAIL_NOT_VERIFIED') {
                    return Promise.reject(error)
                }

                if (error.response?.status === 401 && !originalRequest._retry) {
                    originalRequest._retry = true

                    try {
                        await this.refreshSession()
                        // Retry the original request with new token
                        const token = this.getToken()
                        originalRequest.headers.Authorization = `Bearer ${token}`
                        return axios(originalRequest)
                    } catch (refreshError) {
                        // Refresh failed, redirect to login
                        this.clearAuth()
                        window.location.href = '/login'
                        return Promise.reject(refreshError)
                    }
                }

                return Promise.reject(error)
            }
        )
    }

    handleError(error) {
        if (error.response) {
            // Server responded with error status
            const errorData = error.response.data
            let message = errorData.error || errorData.message || 'An error occurred'
            
            // Provide user-friendly messages for common error codes
            if (errorData.code === 'USER_EXISTS') {
                message = 'An account with this email already exists. Please try logging in instead.'
            } else if (errorData.code === 'INVALID_EMAIL') {
                message = 'Please enter a valid email address.'
            } else if (errorData.code === 'WEAK_PASSWORD') {
                message = 'Password is too weak. Please choose a stronger password.'
            } else if (errorData.code === 'VALIDATION_ERROR') {
                message = 'Please check your information and try again.'
            } else if (errorData.code === 'ROLE_NOT_FOUND') {
                message = 'System error. Please contact support.'
            }
            
            return {
                message: message,
                code: errorData.code,
                status: error.response.status,
                details: errorData
            }
        } else if (error.request) {
            // Request was made but no response received
            return {
                message: 'Network error. Please check your connection and try again.',
                code: 'NETWORK_ERROR',
                status: 0
            }
        } else {
            // Something else happened
            return {
                message: error.message || 'An unexpected error occurred',
                code: 'UNKNOWN_ERROR',
                status: 0
            }
        }
    }
}

// Create and export singleton instance
const authService = new AuthService()
export default authService
