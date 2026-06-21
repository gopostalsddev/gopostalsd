import api from './api';

const normalizeError = (error, fallbackMessage) => {
  return error.response?.data?.error || error.message || fallbackMessage;
};

export const fetchUserOrders = async (userId, params = {}) => {
  try {
    const response = await api.get(`/orders/user/${userId}`, {
      params,
    });

    return response.data;
  } catch (error) {
    throw new Error(normalizeError(error, 'Failed to load user orders'));
  }
};

export const fetchAllOrders = async (params = {}) => {
  try {
    const response = await api.get('/orders/', {
      params,
    });

    return response.data;
  } catch (error) {
    throw new Error(normalizeError(error, 'Failed to load orders'));
  }
};

export const fetchOrder = async (orderId) => {
  try {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  } catch (error) {
    throw new Error(normalizeError(error, 'Failed to load order details'));
  }
};

export const fetchOrderStatuses = async () => {
  try {
    const response = await api.get('/orders/statuses');
    return response.data.statuses || [];
  } catch (error) {
    throw new Error(normalizeError(error, 'Failed to load order statuses'));
  }
};

export const updateOrderStatus = async (orderId, payload) => {
  try {
    const response = await api.put(`/orders/${orderId}/status`, payload);
    return response.data;
  } catch (error) {
    throw new Error(normalizeError(error, 'Failed to update order status'));
  }
};
