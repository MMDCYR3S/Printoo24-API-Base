// src/app/services/shopService.js
import { apiClient } from './apiClient';

export const shopService = {
  // دریافت لیست محصولات
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.categories) {
      filters.categories.forEach(cat => params.append('category', cat));
    }
    if (filters.search) params.append('name', filters.search);
    const response = await apiClient.get('/shop/grid/', { params });
    return response.data;
  },

  // دریافت جزئیات محصول
  getProductDetail: async (slug) => {
    const response = await apiClient.get(`/shop/detail/${slug}/`);
    return response.data;
  },


  calculateLivePrice: async (productId, selections) => {
    const response = await apiClient.post(`/shop/products/${productId}/calculate-price/`, {
      selections: selections
    });
    return response.data;
  }

};