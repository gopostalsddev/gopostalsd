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
  if (price === null || price === undefined || price === '') return 'Price not available';
  const num = parseFloat(price);
  if (isNaN(num)) return 'Price not available';
  return `$${num.toFixed(2)}`;
};

/**
 * Calculate total price based on unit price and quantity
 * @param {string|number} unitPrice - The unit price
 * @param {number} quantity - The quantity
 * @returns {number} Total price
 */
export const calculateTotalPrice = (unitPrice, quantity) => {
  if (unitPrice === null || unitPrice === undefined) return 0;
  const num = parseFloat(unitPrice);
  if (isNaN(num)) return 0;
  return num * quantity;
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
