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
