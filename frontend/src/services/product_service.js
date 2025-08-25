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
        
        return response.data
    }catch (error){
        console.error("Error fetching products: ", error)
        return []
    }
}

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
    return response.data;
  } catch (error) {
    console.error("Error fetching product types: ", error);
    return [];
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

export const checkCategoryClassificationStatus = async (categoryId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/print/categories/${categoryId}/classification-status`);
    return response.data;
  } catch (error) {
    console.error("Error checking classification status: ", error);
    throw error;
  }
};
