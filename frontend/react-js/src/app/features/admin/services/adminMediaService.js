import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/site-media';

export const adminMediaService = {
  getAll: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/`);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}/${id}/`);
    return data;
  },

  create: async (data) => {
    const formData = new FormData();
    formData.append('is_active', data.is_active ? 'True' : 'False');
    
    if (data.file instanceof File) {
      formData.append('file', data.file);
    }
    
    // اگر لینک وارد شده بود
    if (data.link) {
      formData.append('link', data.link);
    }

    const response = await apiClient.post(`${BASE_URL}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  update: async (id, data) => {
    const formData = new FormData();
    
    if (data.is_active !== undefined) {
      formData.append('is_active', data.is_active ? 'True' : 'False');
    }
    
    // در متد PATCH، فقط در صورتی فیلد file ارسال می‌شود که کاربر واقعا یک فایل جدید انتخاب کرده باشد
    if (data.file instanceof File) {
      formData.append('file', data.file);
    }

    if (data.link !== undefined) {
      // اگر کاربر لینک را پاک کرده بود، رشته خالی می‌فرستیم تا در بک‌اند null/خالی شود
      formData.append('link', data.link || '');
    }

    // استفاده از متد PATCH طبق داکیومنت برای ویرایش جزئی
    const response = await apiClient.patch(`${BASE_URL}/${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}/${id}/`);
    return id;
  },
};