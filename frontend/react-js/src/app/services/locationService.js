import { apiClient } from './apiClient';

export const locationService = {
  // دریافت لیست استان‌ها
  getProvinces: async () => {
    const response = await apiClient.get('/order/provinces/'); 
    return response.data;
  },

  // دریافت لیست شهرها بر اساس آیدی استان
  getCities: async (provinceId) => {
    // طبق داکیومنت: /api/v1/order/cities/?province_id=...
    const response = await apiClient.get(`/order/cities/?province_id=${provinceId}`);
    return response.data;
  }
};