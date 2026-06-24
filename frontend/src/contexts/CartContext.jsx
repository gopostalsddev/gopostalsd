import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useAuth } from './AuthContext';
import { api } from '../services/api';

// Cart Context
const CartContext = createContext();

// Cart Actions
const CART_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_CART: 'SET_CART',
  SET_ERROR: 'SET_ERROR',
  ADD_ITEM: 'ADD_ITEM',
  UPDATE_QUANTITY: 'UPDATE_QUANTITY',
  REMOVE_ITEM: 'REMOVE_ITEM',
  CLEAR_CART: 'CLEAR_CART',
  SET_SHIPPING_OPTIONS: 'SET_SHIPPING_OPTIONS',
  SET_SELECTED_SHIPPING: 'SET_SELECTED_SHIPPING'
};

// Initial State
const initialState = {
  cart: {
    id: null,
    items: [],
    subtotal: 0,
    shipping_cost: 0,
    tax_amount: 0,
    total: 0,
    item_count: 0
  },
  shippingOptions: [],
  selectedShipping: null,
  loading: false,
  error: null
};

// Cart Reducer
function cartReducer(state, action) {
  switch (action.type) {
    case CART_ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case CART_ACTIONS.SET_CART:
      return { ...state, cart: action.payload, error: null };
    
    case CART_ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case CART_ACTIONS.ADD_ITEM:
      return { ...state, cart: action.payload };
    
    case CART_ACTIONS.UPDATE_QUANTITY:
      return { ...state, cart: action.payload };
    
    case CART_ACTIONS.REMOVE_ITEM:
      return { ...state, cart: action.payload };
    
    case CART_ACTIONS.CLEAR_CART:
      return { ...state, cart: initialState.cart };
    
    case CART_ACTIONS.SET_SHIPPING_OPTIONS:
      return { ...state, shippingOptions: action.payload };
    
    case CART_ACTIONS.SET_SELECTED_SHIPPING:
      return { ...state, selectedShipping: action.payload };
    
    default:
      return state;
  }
}

// Cart Provider Component
export function CartProvider({ children }) {
  const [state, dispatch] = useReducer(cartReducer, initialState);
  const { isAuthenticated, user } = useAuth();

  // Get session ID (you might want to generate this more robustly)
  const getSessionId = () => {
    let sessionId = sessionStorage.getItem('cart_session_id') || localStorage.getItem('cart_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('cart_session_id', sessionId);
      localStorage.setItem('cart_session_id', sessionId);
    } else {
      // Keep both stores in sync so existing sessions survive storage strategy changes.
      sessionStorage.setItem('cart_session_id', sessionId);
      localStorage.setItem('cart_session_id', sessionId);
    }
    return sessionId;
  };

  // Load cart from server
  const loadCart = async () => {
    if (!isAuthenticated) {
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Please log in to view your cart' });
      return;
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      const response = await api.get(`/cart/?session_id=${sessionId}`);
      
      // Backend returns { success: true, cart: {...} }
      if (response.data && response.data.cart) {
        dispatch({ type: CART_ACTIONS.SET_CART, payload: response.data.cart });
      } else if (response.data) {
        // Fallback if response structure is different
        dispatch({ type: CART_ACTIONS.SET_CART, payload: response.data });
      }
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
    } catch (error) {
      console.error('Error loading cart:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to load cart' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
    }
  };

  // Load cart on mount and when authentication changes
  useEffect(() => {
    // Small delay to ensure auth is fully initialized
    const timer = setTimeout(() => {
      if (isAuthenticated) {
        loadCart();
      }
    }, 100);
    
    return () => clearTimeout(timer);
  }, [isAuthenticated]);

  // Add item to cart
  const addToCart = async (productId, selectedOptions, quantity = 1) => {
    if (!isAuthenticated) {
      return { success: false, error: 'Please log in to add items to your cart' };
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      const response = await api.post('/cart/add', {
        product_id: productId,
        selected_options: selectedOptions,
        quantity: quantity
      }, {
        params: { session_id: sessionId }
      });
      
      // Backend returns the cart object directly (cart_service returns result['cart'])
      if (response.data) {
        dispatch({ type: CART_ACTIONS.SET_CART, payload: response.data });
        dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
        return { success: true };
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to add item to cart' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: false, error: error.response?.data?.error || 'Failed to add item to cart' };
    }
  };

  // Update item quantity
  const updateQuantity = async (cartItemId, quantity) => {
    if (!isAuthenticated) {
      return { success: false, error: 'Please log in to update cart items' };
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      const response = await api.put(`/cart/items/${cartItemId}/quantity`, {
        quantity: quantity
      }, {
        params: { session_id: sessionId }
      });
      
      // Backend returns the cart object directly
      if (response.data && response.data.cart) {
        dispatch({ type: CART_ACTIONS.SET_CART, payload: response.data.cart });
      } else if (response.data) {
        dispatch({ type: CART_ACTIONS.SET_CART, payload: response.data });
      }
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: true };
    } catch (error) {
      console.error('Error updating quantity:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to update quantity' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: false, error: error.response?.data?.error || 'Failed to update quantity' };
    }
  };

  // Remove item from cart
  const removeItem = async (cartItemId) => {
    if (!isAuthenticated) {
      return { success: false, error: 'Please log in to remove cart items' };
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      const response = await api.delete(`/cart/items/${cartItemId}`, {
        params: { session_id: sessionId }
      });
      
      if (response.data) {
        dispatch({ type: CART_ACTIONS.REMOVE_ITEM, payload: response.data });
        dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
        return { success: true };
      }
    } catch (error) {
      console.error('Error removing item:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to remove item' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: false, error: error.response?.data?.error || 'Failed to remove item' };
    }
  };

  // Clear cart
  const clearCart = async () => {
    if (!isAuthenticated) {
      return { success: false, error: 'Please log in to clear your cart' };
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      await api.delete('/cart/clear', {
        params: { session_id: sessionId }
      });
      
      dispatch({ type: CART_ACTIONS.CLEAR_CART });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: true };
    } catch (error) {
      console.error('Error clearing cart:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to clear cart' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: false, error: error.response?.data?.error || 'Failed to clear cart' };
    }
  };

  // Calculate shipping
  const calculateShipping = async (destinationAddress) => {
    if (!isAuthenticated) {
      return { success: false, error: 'Please log in to calculate shipping' };
    }

    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      const sessionId = getSessionId();
      
      const response = await api.post('/cart/shipping', destinationAddress, {
        params: { session_id: sessionId }
      });
      
      if (response.data.success) {
        dispatch({ type: CART_ACTIONS.SET_SHIPPING_OPTIONS, payload: response.data.shipping_options });
        dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
        return { success: true, shippingOptions: response.data.shipping_options };
      } else {
        dispatch({ type: CART_ACTIONS.SET_ERROR, payload: response.data.error });
        dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      console.error('Error calculating shipping:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to calculate shipping' });
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: false });
      return { success: false, error: error.response?.data?.error || 'Failed to calculate shipping' };
    }
  };

  // Set selected shipping option
  const setSelectedShipping = (shippingOption) => {
    dispatch({ type: CART_ACTIONS.SET_SELECTED_SHIPPING, payload: shippingOption });
  };

  // Get cart summary
  const getCartSummary = async () => {
    try {
      const sessionId = getSessionId();
      const response = await api.get(`/cart/summary?session_id=${sessionId}`);
      
      if (response.data) {
        return response.data;
      }
    } catch (error) {
      console.error('Error getting cart summary:', error);
      return {
        item_count: 0,
        subtotal: 0,
        shipping_cost: 0,
        tax_amount: 0,
        total: 0,
        has_items: false
      };
    }
  };

  const value = {
    // State
    cart: state.cart,
    shippingOptions: state.shippingOptions,
    selectedShipping: state.selectedShipping,
    loading: state.loading,
    error: state.error,
    
    // Actions
    loadCart,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    calculateShipping,
    setSelectedShipping,
    getCartSummary
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
}

// Custom hook to use cart context
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}

// Cart utility functions
export const cartUtils = {
  // Format price
  formatPrice: (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  },

  // Calculate item total
  calculateItemTotal: (unitPrice, quantity) => {
    return unitPrice * quantity;
  },

  // Check if cart is empty
  isEmpty: (cart) => {
    return !cart.items || cart.items.length === 0;
  },

  // Get total items count
  getTotalItems: (cart) => {
    if (!cart.items) return 0;
    return cart.items.reduce((total, item) => total + item.quantity, 0);
  },

  // Get cart total with shipping and tax
  getCartTotal: (cart) => {
    const subtotal = cart.subtotal || 0;
    const shipping = cart.shipping_cost || 0;
    const tax = cart.tax_amount || 0;
    return subtotal + shipping + tax;
  }
};
