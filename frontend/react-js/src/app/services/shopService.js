// src/app/services/shopService.js
import { apiClient } from './apiClient';

export const shopService = {
  // دریافت لیست محصولات
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.categories) {
      filters.categories.forEach(cat => params.append('category', cat));
    }
    if (filters.search) params.append('search', filters.search);
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
  },

  // جستجوی محصولات
  // طبق مستندات: GET /api/v1/shop/search/?q=<keyword>
  // این اندپوینت داخل name, description, options جستجو می‌کند و مستقیماً آرایه برمی‌گرداند.
  searchProducts: async (query, page = 1) => {
    const params = new URLSearchParams();
    params.append('q', query);
    // این اندپوینت pagination ندارد → صفحه‌بندی نادیده گرفته می‌شود
    const response = await apiClient.get('/shop/search/', { params });
    // پاسخ مستقیماً آرایه است
    return Array.isArray(response.data) ? response.data : [];
  },
};
