// src/app/services/adminSliderService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/sliders/';

export const adminSliderService = {
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}${id}/`);
    return data;
  },

  create: async (data) => {
    // تبدیل به FormData برای ارسال فایل
    const formData = new FormData();
    formData.append('name', data.name);
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
    formData.append('name', data.name);
    
    // اگر تصویر جدید انتخاب شده باشد ارسال می‌کنیم
    // اگر رشته باشد (URL قبلی)، ارسال نمی‌کنیم
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
};