/**
 * Authentication Service for Go Postal SD Frontend
 * 
 * This service handles all authentication-related API calls and token management.
 */

import axios from 'axios'
import { getApiBaseUrl } from './apiBaseUrl'

const API_BASE_URL = getApiBaseUrl()

const redirectToLogin = () => {
    if (typeof window === 'undefined') {
        return
    }

    window.location.hash = '#/login'
}

/**
 * @typedef {{
 *   message: string,
 *   code: string,
 *   status: number,
 *   errorType: 'HTTP_ERROR' | 'NETWORK_ERROR' | 'TIMEOUT_ERROR' | 'UNKNOWN_ERROR',
 *   isRetryable: boolean,
 *   details?: any,
 * }} AuthServiceError
 */

class AuthService {
    constructor() {
        this.tokenKey = 'gopostalsd_session_token'
        this.refreshTokenKey = 'gopostalsd_refresh_token'
        this.userKey = 'gopostalsd_user'
        this.storage = this.getStorage()

        // Remove legacy persistent auth tokens from localStorage.
        if (typeof window !== 'undefined' && window.localStorage) {
            window.localStorage.removeItem(this.tokenKey)
            window.localStorage.removeItem(this.refreshTokenKey)
            window.localStorage.removeItem(this.userKey)
        }
    }

    /**
     * Build auth headers. CSRF is only attached for state-changing requests.
     * @param {boolean} withContentType
     * @param {boolean} includeCsrfToken
     * @returns {Record<string, string>}
     */
    getAuthHeaders(withContentType = false, includeCsrfToken = false) {
        const headers = {}
        const token = this.getToken()

        if (token) {
            headers.Authorization = `Bearer ${token}`
            if (includeCsrfToken) {
                headers['X-CSRF-Token'] = token
            }
        }

        if (withContentType) {
            headers['Content-Type'] = 'application/json'
        }

        return headers
    }

    getStorage() {
        if (typeof window === 'undefined') {
            return {
                getItem: () => null,
                setItem: () => {},
                removeItem: () => {}
            }
        }

        try {
            return window.sessionStorage
        } catch (_) {
            return {
                getItem: () => null,
                setItem: () => {},
                removeItem: () => {}
            }
        }
    }

    // Token management
    getToken() {
        return this.storage.getItem(this.tokenKey)
    }

    setToken(token) {
        this.storage.setItem(this.tokenKey, token)
    }

    getRefreshToken() {
        return this.storage.getItem(this.refreshTokenKey)
    }

    setRefreshToken(refreshToken) {
        this.storage.setItem(this.refreshTokenKey, refreshToken)
    }

    getUser() {
        const userStr = this.storage.getItem(this.userKey)
        return userStr ? JSON.parse(userStr) : null
    }

    setUser(user) {
        this.storage.setItem(this.userKey, JSON.stringify(user))
    }

    clearAuth() {
        this.storage.removeItem(this.tokenKey)
        this.storage.removeItem(this.refreshTokenKey)
        this.storage.removeItem(this.userKey)
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
            const response = await axios.post(
                `${API_BASE_URL}/auth/verify-email`,
                { token },
                { headers: this.getAuthHeaders(true) }
            )
            return response.data
        } catch (error) {
            console.error('Email verification error:', error)
            throw this.handleError(error)
        }
    }

    async requestEmailVerification(email) {
        try {
            const response = await axios.post(
                `${API_BASE_URL}/auth/resend-verification`,
                { email },
                { headers: this.getAuthHeaders(true) }
            )
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

            // Hydrate full user profile (addresses, status, etc.) after login.
            // The login payload intentionally returns a minimal user object.
            let hydratedUser = user
            try {
                const currentUser = await this.getCurrentUser()
                if (currentUser) {
                    hydratedUser = currentUser
                }
            } catch (profileError) {
                console.warn('Unable to hydrate current user profile after login:', profileError)
            }

            this.setUser(hydratedUser)
            response.data.user = hydratedUser
            
            return {
                ...response.data,
                user: hydratedUser
            }
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
                await axios.post(
                    `${API_BASE_URL}/auth/logout`,
                    { session_token: token },
                        { headers: this.getAuthHeaders(true, true) }
                )
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

            const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken
            }, {
                headers: this.getAuthHeaders(true, true)
            })
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
            }, {
                headers: this.getAuthHeaders(true)
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
            }, {
                headers: this.getAuthHeaders(true)
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

            const response = await axios.get(`${API_BASE_URL}/auth/me`, {
                headers: this.getAuthHeaders()
            })
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
            }, {
                headers: this.getAuthHeaders(true, true)
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
                    if (['post', 'put', 'patch', 'delete'].includes((config.method || '').toLowerCase())) {
                        config.headers['X-CSRF-Token'] = token
                    }
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
                        redirectToLogin()
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
            
            return /** @type {AuthServiceError} */ ({
                message: message,
                code: errorData.code,
                status: error.response.status,
                errorType: 'HTTP_ERROR',
                isRetryable: error.response.status >= 500,
                details: {
                    ...errorData,
                    endpoint: error.config?.url,
                    method: error.config?.method,
                }
            })
        } else if (error.request) {
            // Request was made but no response received
            const timedOut = error.code === 'ECONNABORTED'
            return /** @type {AuthServiceError} */ ({
                message: timedOut
                    ? 'Request timed out. Please try again.'
                    : 'Network error. Please check your connection and try again.',
                code: timedOut ? 'TIMEOUT_ERROR' : 'NETWORK_ERROR',
                status: 0,
                errorType: timedOut ? 'TIMEOUT_ERROR' : 'NETWORK_ERROR',
                isRetryable: true,
                details: {
                    endpoint: error.config?.url,
                    method: error.config?.method,
                }
            })
        } else {
            // Something else happened
            return /** @type {AuthServiceError} */ ({
                message: error.message || 'An unexpected error occurred',
                code: 'UNKNOWN_ERROR',
                status: 0,
                errorType: 'UNKNOWN_ERROR',
                isRetryable: false,
            })
        }
    }
}

// Create and export singleton instance
const authService = new AuthService()
export default authService
