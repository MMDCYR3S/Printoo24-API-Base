import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/tutorials/';

export const adminTutorialService = {
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
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
    const { data } = await apiClient.put(`${BASE_URL}${id}/`, formData, {
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

  bulkStatus: async ({ ids, is_active }) => {
    // ارسال وضعیت گروهی (با توجه به داکیومنت، وضعیت‌های boolean برای این بخش منطقی‌تر است)
    const { data } = await apiClient.patch(`${BASE_URL}bulk-status/`, { 
        ids, 
        is_active,
        status: is_active ? 'published' : 'draft' // برای محکم‌کاری در صورت کپی بودن داکیومنت بک‌اند
    });
    return data;
  },

  getMinimalProducts: async () => {
    const { data } = await apiClient.get('/dashboard/products-minimal/');
    return data;
  }
};