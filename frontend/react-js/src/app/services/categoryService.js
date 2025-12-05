// src/app/services/categoryService.js
import { apiClient } from './apiClient';

export const categoryService = {
  // دریافت درخت کامل دسته‌بندی‌ها (منو)
  getCategoriesTree: async () => {
    const response = await apiClient.get('/shop/categories/');
    return response.data;
  },
  
  // دریافت اطلاعات لندینگ (اگر بعدا برای صفحه اصلی خواستی)
  getCategoriesLanding: async () => {
    const response = await apiClient.get('/shop/categories/landing/');
    return response.data;
  }
};