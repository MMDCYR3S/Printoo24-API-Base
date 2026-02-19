// src/app/services/adminCategoryService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/categories/';

export const adminCategoryService = {
  getRoots: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  getAllSubCategories: async () => {
    const { data } = await apiClient.get(`${BASE_URL}subcategories/`);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}${id}/`);
    return data;
  },

  create: async (formData) => {
    const { data } = await apiClient.post(BASE_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  update: async (id, formData) => {
    const { data } = await apiClient.patch(`${BASE_URL}${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  bulkDelete: async (ids) => {
    await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: { ids } });
    return ids;
  },

  bulkStatus: async ({ ids, active }) => {
    await apiClient.patch(`${BASE_URL}bulk-status/?active=${active}`, { ids });
    return { ids, active };
  },

  // ✅ متد جدید برای عملیات گروهی
bulkUpsert: async (payload) => {
    // در صورتی که payload از نوع FormData باشد، axios اتوماتیک هدر multipart را ست می‌کند
    // اما برای اطمینان بیشتر هدر را صراحتاً ارسال می‌کنیم
    const { data } = await apiClient.post(`${BASE_URL}bulk-upsert/`, payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }
};