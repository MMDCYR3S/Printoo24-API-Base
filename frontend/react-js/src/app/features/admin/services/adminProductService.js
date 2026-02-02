import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/products/';

export const adminProductService = {
  // --- Read ---
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}${id}/`);
    return data;
  },

  getStandardSizes: async () => {
    const { data } = await apiClient.get('/dashboard/sizes/');
    return data;
  },

  getQuantitiesList: async () => {
    const { data } = await apiClient.get('/dashboard/quantities/');
    return data;
  },

  // --- Write (Step 1: Core) ---
  create: async (payload) => {
    // طبق مستندات: POST /api/v1/dashboard/products/
    const { data } = await apiClient.post(BASE_URL, payload);
    return data;
  },

  update: async (id, payload) => {
    // برای ویرایش معمولاً PUT روی ID محصول است
    const { data } = await apiClient.put(`${BASE_URL}${id}/`, payload);
    return data;
  },

  syncOptions: async (id, payload) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/options/`, payload);
    return data;
  },

  // --- Media (Steps 3 & 4) ---
  uploadImage: async (id, formData) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/upload-image/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  uploadAttachment: async (formData) => {
    const { data } = await apiClient.post(`${BASE_URL}upload-attachment/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // --- Bulk ---
  bulkDelete: async (product_ids) => {
    const { data } = await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: product_ids });
    return data;
  },

  bulkStatus: async ({ product_ids, is_active }) => {
    const { data } = await apiClient.patch(`${BASE_URL}bulk-status/`, { product_ids, is_active });
    return data;
  },
};