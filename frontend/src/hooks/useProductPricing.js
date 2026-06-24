import { useState, useEffect } from 'react';
import { calculateProductPrice } from '../services/product_service';

/**
 * Custom hook for managing product pricing
 * Follows Single Responsibility Principle
 */
export const useProductPricing = (productId, selectedOptions, options, customization = null) => {
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const customizationKey = customization ? JSON.stringify(customization) : '';

  const hasSelectedValue = (value) =>
    value !== undefined && value !== null && `${value}` !== '';

  useEffect(() => {
    const calculatePrice = async () => {
      if (!productId || Object.keys(selectedOptions).length === 0) {
        setPricing(null);
        return;
      }

      // Check if all required option groups have selections
      const hasAllRequiredOptions = options.every(optionGroup =>
        hasSelectedValue(selectedOptions[optionGroup.group])
      );

      if (!hasAllRequiredOptions) {
        setPricing(null);
        return;
      }

      // Generate the option key in the correct order
      const optionIds = options.map(optionGroup => 
        selectedOptions[optionGroup.group]
      ).filter(hasSelectedValue);

      if (optionIds.length === 0) {
        setPricing(null);
        return;
      }

      setLoading(true);
      setError(null);
      
      try {
        const priceData = await calculateProductPrice(parseInt(productId), optionIds, 6, customization);
        if (!priceData || typeof priceData.price !== 'number') {
          setError('Price is currently unavailable for this configuration. Please try a different option set.');
          setPricing(null);
          return;
        }
        setPricing(priceData);
      } catch (error) {
        console.error('Error calculating price:', error);
        setError(error?.message || 'Failed to calculate price');
        setPricing(null);
      } finally {
        setLoading(false);
      }
    };

    calculatePrice();
  }, [productId, selectedOptions, options, customizationKey]);

  return { pricing, loading, error };
};
