// src/app/services/shopService.js
import { apiClient } from './apiClient';

export const shopService = {
  // دریافت لیست محصولات بر اساس فیلترهای URL
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();

    // فیلتر دسته‌بندی‌ها (ارسال چندباره کلید در صورت نیاز بک‌اند)
    if (filters.categories && Array.isArray(filters.categories)) {
      filters.categories.forEach(cat => {
        if (cat) params.append('category', cat);
      });
    }

    // فیلتر جستجوی متنی
    if (filters.search) {
      params.append('name', filters.search);
    }

    // آدرس دقیق بر اساس داکیومنت شما
    const response = await apiClient.get('/shop/grid/', { params });
    return response.data;
  },

  // دریافت جزئیات یک محصول با اسلاگ
  getProductDetail: async (slug) => {
    const response = await apiClient.get(`/shop/detail/${slug}/`);
    return response.data;
  }
};