// src/app/services/adminArticleService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/articles/';

export const adminArticleService = {
  // دریافت لیست مقالات
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  // دریافت جزئیات یک مقاله
  getById: async (id) => {
    const { data } = await apiClient.get(`${BASE_URL}${id}/`);
    return data;
  },

  // ایجاد مقاله (پشتیبانی از تصویر)
  create: async (formData) => {
    const { data } = await apiClient.post(BASE_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // ویرایش مقاله
  update: async (id, formData) => {
    // از PUT استفاده شده طبق داکیومنت شما، اما فرم‌دیتا ارسال می‌شود
    const { data } = await apiClient.put(`${BASE_URL}${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // حذف تکی
  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  // حذف گروهی
  bulkDelete: async (ids) => {
    await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: { ids } });
    return ids;
  },

  // تغییر وضعیت گروهی
  bulkStatus: async ({ ids, status }) => {
    const { data } = await apiClient.patch(`${BASE_URL}bulk-status/`, { ids, status });
    return data;
  },

  // انتشار سریع یک مقاله
  quickPublish: async (id) => {
    const { data } = await apiClient.patch(`${BASE_URL}${id}/publish/`);
    return data;
  },

  // دریافت محصولات برای دراپ‌داون مقالات
  getMinimalProducts: async () => {
    const { data } = await apiClient.get('/dashboard/products-minimal/');
    return data;
  }
};