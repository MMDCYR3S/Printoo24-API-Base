// src/app/services/adminModalService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/modals/';

export const adminModalService = {
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  create: async (data) => {
    const formData = new FormData();
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    if (data.cta_text) formData.append('cta_text', data.cta_text);
    if (data.cta_url) formData.append('cta_url', data.cta_url);
    // وضعیت پیش‌فرض معمولا true است مگر اینکه در فرم تعیین شود
    formData.append('is_active', data.is_active); 

    if (data.image) {
      formData.append('image', data.image);
    }

    const response = await apiClient.post(BASE_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  update: async (id, data) => {
    const formData = new FormData();
    formData.append('title', data.title);
    if (data.description) formData.append('description', data.description);
    if (data.cta_text) formData.append('cta_text', data.cta_text);
    if (data.cta_url) formData.append('cta_url', data.cta_url);
    formData.append('is_active', data.is_active);

    // ارسال تصویر فقط اگر فایل جدید انتخاب شده باشد
    if (data.image && typeof data.image !== 'string') {
      formData.append('image', data.image);
    }

    const response = await apiClient.patch(`${BASE_URL}${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  // متد اختصاصی تغییر وضعیت
  toggleStatus: async (id) => {
    const { data } = await apiClient.post(`${BASE_URL}${id}/toggle-status/`);
    return data;
  },
};