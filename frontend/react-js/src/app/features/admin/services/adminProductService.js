// src/app/features/admin/products/services/adminProductService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/products/';

export const adminProductService = {
  // ✅ 1. متد لیست‌گیری (این پاک شده بود!)
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  // --- مرحله ۱: ایجاد و ویرایش هسته محصول ---
  create: async (data) => {
    const response = await apiClient.post(BASE_URL, data);
    return response.data;
  },

  getById: async (id) => {
    const response = await apiClient.get(`${BASE_URL}${id}/`);
    return response.data;
  },

  update: async (id, data) => {
    const response = await apiClient.put(`${BASE_URL}${id}/`, data);
    return response.data;
  },

  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  // --- مرحله ۲: مدیریت آپشن‌ها (ویژگی‌ها) ---
  syncOptions: async (id, payload) => {
    const response = await apiClient.post(`${BASE_URL}${id}/options/`, payload);
    return response.data;
  },

  updateOptionConfig: async (id, payload) => {
    const response = await apiClient.patch(`${BASE_URL}${id}/update-option-config/`, payload);
    return response.data;
  },

  deleteOption: async (id, optionId) => {
    await apiClient.delete(`${BASE_URL}${id}/options/${optionId}/`);
    return optionId;
  },

  // --- مرحله ۳: مدیریت تصاویر و فایل‌ها ---
  uploadImage: async (id, formData) => {
    const response = await apiClient.post(`${BASE_URL}${id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  syncMedia: async (id, payload) => {
    const response = await apiClient.post(`${BASE_URL}${id}/media-sync/`, payload);
    return response.data;
  },

  // --- عملیات گروهی ---
  bulkDelete: async (product_ids) => {
    const response = await apiClient.delete(`${BASE_URL}bulk-delete/`, {
      data: product_ids 
    });
    return response.data;
  },

  bulkStatus: async ({ product_ids, is_active }) => {
    const response = await apiClient.patch(`${BASE_URL}bulk-status/`, {
      product_ids,
      is_active
    });
    return response.data;
  },
};