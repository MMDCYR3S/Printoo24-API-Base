// src/app/features/admin/services/adminMasterDataService.js
import { apiClient } from '../../../services/apiClient';

export const adminMasterDataService = {
  // === 📏 مدیریت سایزها ===
  getSizes: async () => {
    const response = await apiClient.get('/dashboard/sizes/');
    return response.data;
  },

  addSize: async (data) => {
    // data: { name, width, height }
    const response = await apiClient.post('/dashboard/sizes/', data);
    return response.data;
  },

  updateSize: async ({ id, data }) => {
    const response = await apiClient.put(`/dashboard/sizes/${id}/`, data);
    return response.data;
  },

  deleteSize: async (id) => {
    await apiClient.delete(`/dashboard/sizes/${id}/`);
  },

  // === 🔢 مدیریت تیراژها ===
  getQuantities: async () => {
    const response = await apiClient.get('/dashboard/quantities/');
    return response.data;
  },

  addQuantity: async (data) => {
    // data: { value }
    const response = await apiClient.post('/dashboard/quantities/', data);
    return response.data;
  },

  updateQuantity: async ({ id, data }) => {
    const response = await apiClient.put(`/dashboard/quantities/${id}/`, data);
    return response.data;
  },

  deleteQuantity: async (id) => {
    await apiClient.delete(`/dashboard/quantities/${id}/`);
  },
};