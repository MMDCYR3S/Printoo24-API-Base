// src/app/services/cartService.js (جدید)
import { apiClient } from './apiClient';

export const cartService = {
  addToCart: async (payload) => {
    // payload باید دقیقاً طبق مستندات سرور باشد
    const response = await apiClient.post('/cart/add/item/', payload);
    return response.data;
  }
};