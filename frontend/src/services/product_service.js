import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

export const fetchPrintProductCategories = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/print/categories`);
        return response.data;
    } catch (error) {
        console.error("Error fetching categories: ", error);
        return []
    }
};


export const updatePrintProductCategoryStatus = async (categoryId, enabled) => {
    try {
        const response = await axios.put(`${API_BASE_URL}/print/categories/${categoryId}/status`, { enabled })
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