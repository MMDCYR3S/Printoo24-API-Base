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
  },

  // دریافت جزئیات محصول
  getProductDetail: async (slug) => {
    const response = await apiClient.get(`/shop/detail/${slug}/`);
    return response.data;
  },

  /**
   * جستجوی پیشرفته محصولات با پشتیبانی از صفحه‌بندی
   * @param {string} query - کلمه کلیدی
   * @param {number} page - شماره صفحه برای اسکرول نامحدود
   */

  searchProducts: async (query, page = 1) => {
    if (!query) return [];
    const response = await apiClient.get('/shop/search/', {
      params: { 
        q: query,
        page: page // آماده‌سازی برای اسکرول نامحدود در صورت پشتیبانی بک‌اند
      }
    });
    return response.data;
  },
};