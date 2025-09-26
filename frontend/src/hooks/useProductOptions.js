import { useState, useEffect } from 'react';
import { fetchProductOptions } from '../services/product_service';

/**
 * Custom hook for managing product options
 * Follows Single Responsibility Principle
 */
export const useProductOptions = (productId) => {
  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadOptions = async () => {
      if (!productId) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const productOptions = await fetchProductOptions(parseInt(productId), 6);
        setOptions(productOptions);
      } catch (error) {
        console.error('Error loading product options:', error);
        setError('Failed to load product options');
      } finally {
        setLoading(false);
      }
    };

    loadOptions();
  }, [productId]);

  return { options, loading, error };
};
