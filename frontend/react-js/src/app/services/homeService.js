// src/app/services/homeService.js
import { apiClient } from './apiClient';

export const homeService = {
  // دریافت لیست اسلایدرها
  getSliders: async () => {
    // طبق مستندات: GET /api/v1/home/sliders/
    const response = await apiClient.get('/home/sliders/');
    return response.data;
  },
};