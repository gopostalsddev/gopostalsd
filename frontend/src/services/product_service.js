import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const fetchPrintProductCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/print/categories/all`);
        return response.data;
    } catch (error) {
        console.error("Error fetching categories: ", error);
        return []
    }
};

export const fetchEnabledPrintProductCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/print/categories`);
        return response.data;
    } catch (error) {
        console.error("Error fetching enabled categories: ", error);
        return []
    }
};

export const updatePrintProductCategoryStatus = async (categoryId, enabled) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/print/categories/${categoryId}/status?enabled=${enabled}`)
        return response.data
    } catch (error) {
        console.error("Error updating category status:", error);
        throw error;
    }
};

export const syncPrintProductCategories = async () => {
    try {
        const response = await axios.post(`${API_BASE_URL}/print/categories/sync`)
        return response.data;
    }catch (error) {
        console.error("Error syncing categories:", error)
    }
};

export const fetchEnabledPrintProductsByCategory = async (category_id) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/print/products/${category_id}`)
        return response.data
    } catch (error) {
        console.error("Error fetching enabled products: ", error)
        return []
    }
}

export const fetchAllPrintProductsByCategory = async (category_id) => {
    
    try{
        const response = await axios.get(`${API_BASE_URL}/print/products/${category_id}/all`)
        
        return { success: true, data: response.data }
    }catch (error){
        console.error("Error fetching products: ", error)
        return { success: false, data: [] }
    }
}

export const fetchProductsByType = async (typeId) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/print/products/type/${typeId}`);
        return { success: true, data: response.data };
    } catch (error) {
        console.error("Error fetching products by type: ", error);
        return { success: false, data: [] };
    }
};

export const updatePrintProductCategoryDetails = async (categoryDetails) => {
  try {
    const formData = new FormData();

    if (categoryDetails.description) {
      formData.append("description", categoryDetails.description);
    }

    if (categoryDetails.imageFile) {
      formData.append("image", categoryDetails.imageFile);
    }

    const response = await axios.put(
      `${API_BASE_URL}/print/categories/${categoryDetails.id}/update`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.status === 200;
  } catch (error) {
    console.error("Failed to update product category details:", error);
    return false;
  }
};

export const updatePrintProductDetails = async (productDetails) => {
  try {
    const formData = new FormData();

    if (productDetails.description) {
      formData.append("description", productDetails.description);
    }

    if (productDetails.imageFile) {
      formData.append("image", productDetails.imageFile);
    }

    const response = await axios.put(
      `${API_BASE_URL}/print/products/${productDetails.id}/update`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.status === 200;
  } catch (error) {
    console.error("Failed to update product details:", error);
    return false;
  }
};

// Product Type API functions
export const fetchAllProductTypes = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/print/product-types`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error("Error fetching product types: ", error);
    return { success: false, data: [] };
  }
};

export const fetchProductTypesByCategory = async (categoryId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/print/product-types/category/${categoryId}`);
    return { success: true, data: response.data };
  } catch (error) {
    console.error("Error fetching product types by category: ", error);
    return { success: false, data: [] };
  }
};

export const createProductType = async (productTypeData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/print/product-types`, productTypeData);
    return response.data;
  } catch (error) {
    console.error("Error creating product type: ", error);
    
    // Enhanced error logging
    if (error.response) {
      console.error("Error response status:", error.response.status);
      console.error("Error response data:", error.response.data);
    }
    
    // Re-throw with more context
    const errorMessage = error.response?.data?.error || error.message || "Unknown error occurred";
    throw new Error(`Failed to create product type: ${errorMessage}`);
  }
};

export const updateProductType = async (typeId, productTypeData) => {
  try {
    const formData = new FormData();

    if (productTypeData.description) {
      formData.append("description", productTypeData.description);
    }

    if (productTypeData.imageFile) {
      formData.append("image", productTypeData.imageFile);
    }

    const response = await axios.put(
      `${API_BASE_URL}/print/product-types/${typeId}/update`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.status === 200;
  } catch (error) {
    console.error("Failed to update product type details:", error);
    return false;
  }
};

export const deleteProductType = async (typeId) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/print/product-types/${typeId}/delete`);
    return response.status === 200;
  } catch (error) {
    console.error("Error deleting product type: ", error);
    throw error;
  }
};

// Product classification functions
export const assignProductToType = async (productId, typeId) => {
  try {
    const response = await axios.put(
      `${API_BASE_URL}/print/products/${productId}/assign-type`, 
      { type_id: typeId },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    return response.status === 200;
  } catch (error) {
    console.error("Error assigning product to type: ", error);
    if (error.response) {
      console.error("Error response status:", error.response.status);
      console.error("Error response data:", error.response.data);
      console.error("Error response headers:", error.response.headers);
    }
    throw error; // Re-throw to let the component handle it
  }
};

export const unassignProductFromType = async (productId) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/print/products/${productId}/unassign-type`);
    return response.status === 200;
  } catch (error) {
    console.error("Error unassigning product from type: ", error);
    return false;
  }
};



export const syncProductsForCategory = async (categoryId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/print/categories/${categoryId}/sync-products`);
    return response.data;
  } catch (error) {
    console.error("Error syncing products for category: ", error);
    if (error.response) {
      console.error("Error response status:", error.response.status);
      console.error("Error response data:", error.response.data);
    }
    throw error;
  }
};

export const fetchAllVendors = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/print/vendors`);
    return response.data;
  } catch (error) {
    console.error("Error fetching vendors: ", error);
    throw error;
  }
};

// Pricing and Cart API functions
export const fetchProductOptions = async (productId, storeCode = 6) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/pricing/products/${productId}/options?store_code=${storeCode}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching product options: ", error);
    return [];
  }
};

export const calculateProductPrice = async (productId, options, storeCode = 6) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/pricing/products/${productId}/price`, {
      product_id: productId,
      options: options,
      store_code: storeCode
    });
    return response.data;
  } catch (error) {
    console.error("Error calculating product price: ", error);
    return null;
  }
};

export const fetchProductVariants = async (productId, offset = 0) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/pricing/products/${productId}/variants?offset=${offset}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching product variants: ", error);
    return { variants: [], count: 0 };
  }
};

export const getOrCreateCart = async (sessionId, userId = null, storeCode = 6) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/cart?session_id=${sessionId}&user_id=${userId}&store_code=${storeCode}`);
    return response.data;
  } catch (error) {
    console.error("Error getting/creating cart: ", error);
    return null;
  }
};

export const addItemToCart = async (cartId, productId, productName, productSku, selectedOptions, quantity = 1) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/cart/${cartId}/items`, {
      product_id: productId,
      product_name: productName,
      product_sku: productSku,
      selected_options: selectedOptions,
      quantity: quantity
    });
    return response.data;
  } catch (error) {
    console.error("Error adding item to cart: ", error);
    return null;
  }
};

export const updateCartItemQuantity = async (cartItemId, quantity) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/cart/items/${cartItemId}?quantity=${quantity}`);
    return response.data;
  } catch (error) {
    console.error("Error updating cart item quantity: ", error);
    return null;
  }
};

export const removeCartItem = async (cartItemId) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/cart/items/${cartItemId}`);
    return response.data;
  } catch (error) {
    console.error("Error removing cart item: ", error);
    return null;
  }
};

export const getCartTotals = async (cartId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/cart/${cartId}/totals`);
    return response.data;
  } catch (error) {
    console.error("Error getting cart totals: ", error);
    return { subtotal: 0, tax: 0, total: 0, item_count: 0 };
  }
};

export const getShippingEstimates = async (requestData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/pricing/shipping/estimates`, requestData);
    return response.data;
  } catch (error) {
    console.error("Error getting shipping estimates: ", error);
    throw error;
  }
};