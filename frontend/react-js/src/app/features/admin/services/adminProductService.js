import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/products/';

export const adminProductService = {
  // --- Read (خواندن اطلاعات) ---
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}${id}/`);
    return data;
  },

  // --- Step 1: Core (مدیریت هسته محصول) ---
  create: async (payload) => {
    const { data } = await apiClient.post(BASE_URL, payload);
    return data;
  },

  update: async (id, payload) => {
    const { data } = await apiClient.put(`${BASE_URL}${id}/`, payload);
    return data;
  },

  // --- Step 2: Form Builder (همگام‌سازی فیلدها و شرط‌ها) ---
  syncFields: async (id, payload) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/sync-fields/`, payload);
    return data;
  },

  // --- Step 3: Formula Builder (همگام‌سازی فرمول‌های قیمت) ---
  syncFormulas: async (id, payload) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/sync-formulas/`, payload);
    return data;
  },

  // --- Step 4: Media & Attachments (مدیریت رسانه) ---
  uploadImage: async (id, formData) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  uploadAttachment: async (formData) => {
    // طبق سواگر برای اتچمنت آیدی محصول در بدنه ارسال می‌شود نه در URL
    const { data } = await apiClient.post(`${BASE_URL}upload-attachment/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // --- Bulk Actions (عملیات گروهی) ---
  bulkDelete: async (product_ids) => {
    const { data } = await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: product_ids });
    return data;
  },

  bulkStatus: async ({ product_ids, is_active }) => {
    const { data } = await apiClient.patch(`${BASE_URL}bulk-status/`, { product_ids, is_active });
    return data;
  }
};