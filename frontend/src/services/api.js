/**
 * API Service for Go Postal SD Frontend
 * 
 * This service provides a centralized axios instance for all API calls.
 */

import axios from 'axios';
import { getApiBaseUrl } from './apiBaseUrl';

const API_BASE_URL = getApiBaseUrl();

const redirectToLogin = () => {
  if (typeof window === 'undefined') {
    return;
  }

  window.location.hash = '#/login';
};

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
    const skipAuth = config.skipAuth === true;

    if (skipAuth) {
      return config;
    }

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
    const skipAuth = error.config?.skipAuth === true;
    if (error.response?.status === 401 && !skipAuth) {
      // Token expired or invalid
      const storage = getAuthStorage();
      storage.removeItem('gopostalsd_session_token');
      storage.removeItem('gopostalsd_refresh_token');
      storage.removeItem('gopostalsd_user');
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);

export { api };
export default api;
