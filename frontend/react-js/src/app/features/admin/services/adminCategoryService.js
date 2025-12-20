// src/app/services/adminCategoryService.js
import apiClient from '../../../services/apiClient'; // فرض بر این است که اینستنس Axios شماست

const BASE_URL = '/dashboard/categories/';

export const adminCategoryService = {
  // دریافت لیست (می‌تواند شامل فیلترهای کوئری باشد)
  getAll: async (params = {}) => {
    const { data } = await apiClient.get(BASE_URL, { params });
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

  // --- عملیات گروهی ---
  bulkDelete: async (ids) => {
    // طبق داکیومنت، متد DELETE بادی می‌گیرد (استاندارد REST مدرن)
    await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: { ids } });
    return ids;
  },

  bulkStatus: async ({ ids, active }) => {
    // طبق داکیومنت: active کوئری پارامتر است، ids در بادی
    await apiClient.patch(`${BASE_URL}bulk-status/?active=${active}`, { ids });
    return { ids, active };
  },
};