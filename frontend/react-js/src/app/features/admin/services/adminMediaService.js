import apiClient from '../../../services/apiClient';

// تغییر مهم: اسلش آخر رو برداشتم تا اگر مشکل ریدایرکت 301 بود حل شود
// اگر با حذف اسلش ارور 404 یا 301 گرفتید، مجدد اسلش را بگذارید
const BASE_URL = '/dashboard/site-media'; 

export const adminMediaService = {
  getAll: async () => {
    // برای GET معمولا اسلش آخر در انتهای URL قرار می‌گیرد
    const { data } = await apiClient.get(`${BASE_URL}/`);
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}/${id}/`);
    return data;
  },

  create: async (data) => {
    const formData = new FormData();
    
    // تبدیل امن بولین برای بک‌اند
    formData.append('is_active', data.is_active ? 'True' : 'False');
    
    if (data.file) {
      formData.append('file', data.file);
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
    
    if (data.file && typeof data.file !== 'string') {
      formData.append('file', data.file);
    }

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