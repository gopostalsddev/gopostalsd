import { useCart } from '../contexts/CartContext';

/**
 * Custom hook for cart operations
 * Provides convenient methods for cart management
 */
export function useCartOperations() {
  const {
    cart,
    loading,
    error,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    calculateShipping,
    setSelectedShipping,
    getCartSummary
  } = useCart();

  // Add item to cart with error handling
  const addItemToCart = async (productId, selectedOptions, quantity = 1) => {
    try {
      const result = await addToCart(productId, selectedOptions, quantity);
      if (result.success) {
        return { success: true, message: 'Item added to cart successfully' };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'Failed to add item to cart' };
    }
  };

  // Update item quantity with validation
  const updateItemQuantity = async (cartItemId, quantity) => {
    if (quantity < 0) {
      return { success: false, error: 'Quantity cannot be negative' };
    }
    
    if (quantity === 0) {
      return await removeItemFromCart(cartItemId);
    }

    try {
      const result = await updateQuantity(cartItemId, quantity);
      if (result.success) {
        return { success: true, message: 'Quantity updated successfully' };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'Failed to update quantity' };
    }
  };

  // Remove item from cart
  const removeItemFromCart = async (cartItemId) => {
    try {
      const result = await removeItem(cartItemId);
      if (result.success) {
        return { success: true, message: 'Item removed from cart successfully' };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'Failed to remove item from cart' };
    }
  };

  // Clear entire cart
  const clearEntireCart = async () => {
    try {
      const result = await clearCart();
      if (result.success) {
        return { success: true, message: 'Cart cleared successfully' };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'Failed to clear cart' };
    }
  };

  // Calculate shipping with validation
  const calculateShippingOptions = async (destinationAddress) => {
    if (!destinationAddress) {
      return { success: false, error: 'Destination address is required' };
    }

    const requiredFields = ['street', 'city', 'state', 'zip_code', 'country'];
    const missingFields = requiredFields.filter(field => !destinationAddress[field]);
    
    if (missingFields.length > 0) {
      return { 
        success: false, 
        error: `Missing required fields: ${missingFields.join(', ')}` 
      };
    }

    try {
      const result = await calculateShipping(destinationAddress);
      if (result.success) {
        return { 
          success: true, 
          shippingOptions: result.shippingOptions,
          message: 'Shipping options calculated successfully'
        };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: 'Failed to calculate shipping options' };
    }
  };

  // Get cart statistics
  const getCartStats = () => {
    const itemCount = cart.items?.length || 0;
    const totalItems = cart.items?.reduce((total, item) => total + item.quantity, 0) || 0;
    const subtotal = cart.subtotal || 0;
    const shipping = cart.shipping_cost || 0;
    const tax = cart.tax_amount || 0;
    const total = subtotal + shipping + tax;

    return {
      itemCount,
      totalItems,
      subtotal,
      shipping,
      tax,
      total,
      isEmpty: itemCount === 0,
      hasItems: itemCount > 0
    };
  };

  // Check if item exists in cart
  const isItemInCart = (productId, selectedOptions) => {
    if (!cart.items) return false;
    
    return cart.items.some(item => {
      if (item.product_id !== productId) return false;
      
      // Compare selected options
      const itemOptions = JSON.stringify(item.selected_options);
      const targetOptions = JSON.stringify(selectedOptions);
      
      return itemOptions === targetOptions;
    });
  };

  // Get item from cart
  const getCartItem = (productId, selectedOptions) => {
    if (!cart.items) return null;
    
    return cart.items.find(item => {
      if (item.product_id !== productId) return false;
      
      const itemOptions = JSON.stringify(item.selected_options);
      const targetOptions = JSON.stringify(selectedOptions);
      
      return itemOptions === targetOptions;
    });
  };

  return {
    // State
    cart,
    loading,
    error,
    
    // Actions
    addItemToCart,
    updateItemQuantity,
    removeItemFromCart,
    clearEntireCart,
    calculateShippingOptions,
    setSelectedShipping,
    getCartSummary,
    
    // Utilities
    getCartStats,
    isItemInCart,
    getCartItem
  };
}

/**
 * Hook for cart display formatting
 */
export function useCartFormatting() {
  const { cart } = useCart();

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price || 0);
  };

  // Format cart totals
  const formatCartTotals = () => {
    const subtotal = cart.subtotal || 0;
    const shipping = cart.shipping_cost || 0;
    const tax = cart.tax_amount || 0;
    const total = subtotal + shipping + tax;

    return {
      subtotal: formatPrice(subtotal),
      shipping: formatPrice(shipping),
      tax: formatPrice(tax),
      total: formatPrice(total),
      raw: { subtotal, shipping, tax, total }
    };
  };

  // Format item options for display
  const formatItemOptions = (selectedOptions) => {
    if (!selectedOptions) return '';
    
    return Object.entries(selectedOptions)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ');
  };

  // Get cart summary text
  const getCartSummaryText = () => {
    const itemCount = cart.items?.length || 0;
    const totalItems = cart.items?.reduce((total, item) => total + item.quantity, 0) || 0;
    
    if (itemCount === 0) {
      return 'Your cart is empty';
    } else if (itemCount === 1) {
      return `1 item (${totalItems} total)`;
    } else {
      return `${itemCount} items (${totalItems} total)`;
    }
  };

  return {
    formatPrice,
    formatCartTotals,
    formatItemOptions,
    getCartSummaryText
  };
}
