import { apiClient } from './apiClient';

export const cartService = {
  // افزودن آیتم
  addToCart: async (payload) => {
    const response = await apiClient.post('/cart/add/item/', payload);
    return response.data;
  },

  // دریافت جزئیات یک آیتم خاص (برای نمایش فایل‌های آپلود شده قبلی)
  getItem: async (itemId) => {
    const response = await apiClient.get(`/cart/item/${itemId}/`);
    return response.data;
  },

  // آپلود فایل (تکی)
  uploadDesign: async (itemId, file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(`/cart/items/${itemId}/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // حذف آیتم
  deleteItem: async (itemId) => {
     await apiClient.delete(`/cart/delete/${itemId}/`);
  },

  // دریافت کل سبد
  getCartItems: async () => {
    const response = await apiClient.get('/cart/items/');
    return response.data;
  },

  getTotalNumber: async () => {
    const Total = await apiClient.get('/cart/items')
    return Total.data.total_items
  }
};