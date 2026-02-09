// src/app/services/adminCategoryService.js
import apiClient from '../../../services/apiClient'; // مسیر ایمپورت را چک کنید

const BASE_URL = '/dashboard/categories/';

export const adminCategoryService = {
  // دریافت لیست والدها (ریشه‌ها)
  getRoots: async () => {
    // معمولا اندپوینت پیش‌فرض ریشه‌ها را می‌دهد
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  // دریافت لیست کامل زیردسته‌ها (برای تب زیردسته‌ها)
  // فرض: بک‌اند فیلتری دارد یا لیست فلت را برمی‌گرداند. 
  // اگر بک‌اند جنگو باشد معمولا parent__isnull=false کار می‌کند
  getAllSubCategories: async () => {
    const { data } = await apiClient.get(BASE_URL, { 
      params: { parent__isnull: false } 
    });
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
};