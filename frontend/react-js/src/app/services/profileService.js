// src/app/services/profileService.js
import { apiClient } from './apiClient';

export const profileService = {
  // 👤 اطلاعات کاربری
  getProfileInfo: async () => {
    const response = await apiClient.get('/profile/info/');
    return response.data;
  },

  updateProfileInfo: async (data) => {
    const response = await apiClient.put('/profile/info/', data);
    return response.data;
  },

  // 💰 کیف پول
  getWalletBalance: async () => {
    const response = await apiClient.get('/profile/wallet/');
    return response.data;
  },

  getWalletHistory: async () => {
    const response = await apiClient.get('/profile/wallet/history/');
    return response.data; // آرایه‌ای از تراکنش‌ها
  },

  // 📦 سفارشات
  getOrders: async () => {
    const response = await apiClient.get('/profile/orders/');
    return response.data; // لیست خلاصه
  },

  getOrderDetails: async (orderId) => {
    const response = await apiClient.get(`/profile/orders/${orderId}/`);
    return response.data; // جزئیات کامل
  },

  // دریافت پیش‌فاکتور (جدید)
  getQuotation: async (orderId) => {
    const response = await apiClient.get(`/profile/orders/quotation/${orderId}/`);
    return response.data;
  },

  // 🌍 موقعیت مکانی (استان و شهر)
  getProvinces: async () => {
    const response = await apiClient.get('/profile/locations/provinces/');
    return response.data;
  },

  getCities: async (provinceId) => {
    if (!provinceId) return [];
    const response = await apiClient.get('/profile/locations/cities/', {
      params: { province_id: provinceId }
    });
    return response.data;
  },

  // 📍 آدرس‌ها
  getAddresses: async () => {
    const response = await apiClient.get('/profile/addresses/');
    return response.data;
  },

  addAddress: async (data) => {
    const response = await apiClient.post('/profile/addresses/', data);
    return response.data;
  },

  updateAddress: async (id, data) => {
    const response = await apiClient.put(`/profile/addresses/${id}/`, data);
    return response.data;
  },

  deleteAddress: async (id) => {
    await apiClient.delete(`/profile/addresses/${id}/`);
  }
};