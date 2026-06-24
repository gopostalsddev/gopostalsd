/**
 * API Service for Go Postal SD Frontend
 * 
 * This service provides a centralized axios instance for all API calls.
 */

import axios from 'axios';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? '/api' : 'http://localhost:5000/api');

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const getAuthStorage = () => {
  if (typeof window === 'undefined') {
    return {
      getItem: () => null,
      removeItem: () => {},
    };
  }

  try {
    return window.sessionStorage;
  } catch (_) {
    return {
      getItem: () => null,
      removeItem: () => {},
    };
  }
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAuthStorage().getItem('gopostalsd_session_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      if (['post', 'put', 'patch', 'delete'].includes((config.method || '').toLowerCase())) {
        config.headers['X-CSRF-Token'] = token;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      const storage = getAuthStorage();
      storage.removeItem('gopostalsd_session_token');
      storage.removeItem('gopostalsd_refresh_token');
      storage.removeItem('gopostalsd_user');
      // Optionally redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export { api };
export default api;
