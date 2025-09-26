/**
 * Utility functions for price formatting and calculations
 * Follows Single Responsibility Principle
 */

/**
 * Format price for display
 * @param {string|number} price - The price to format
 * @returns {string} Formatted price string
 */
export const formatPrice = (price) => {
  if (!price) return 'Price not available';
  return `$${parseFloat(price).toFixed(2)}`;
};

/**
 * Calculate total price based on unit price and quantity
 * @param {string|number} unitPrice - The unit price
 * @param {number} quantity - The quantity
 * @returns {number} Total price
 */
export const calculateTotalPrice = (unitPrice, quantity) => {
  if (!unitPrice) return 0;
  return parseFloat(unitPrice) * quantity;
};

/**
 * Get estimated ship date (3 business days from today)
 * @returns {string} Formatted date string
 */
export const getEstimatedShipDate = () => {
  const today = new Date();
  const shipDate = new Date(today);
  shipDate.setDate(today.getDate() + 3); // 3 business days
  return shipDate.toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};
