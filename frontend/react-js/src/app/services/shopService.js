import { apiClient } from './apiClient';

export const shopService = {
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();

    // مدیریت مولتی سلکت: ارسال چندباره‌ی کلید category
    // مثال خروجی: ?category=slug1&category=slug2
    if (filters.categories && Array.isArray(filters.categories)) {
      filters.categories.forEach(cat => {
        if (cat) params.append('category', cat);
      });
    }

    // جستجو
    if (filters.search) {
      params.append('name', filters.search);
    }

    const response = await apiClient.get('/shop/grid/', { params });
    return response.data;
  },

  getProductDetail: async (slug) => {
    const response = await apiClient.get(`/shop/detail/${slug}/`);
    return response.data;
  }
};