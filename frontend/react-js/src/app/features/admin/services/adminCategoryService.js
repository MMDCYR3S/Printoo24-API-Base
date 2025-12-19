// src/app/services/adminCategoryService.js
import apiClient from '../../../services/apiClient'; // فرض بر این است که اینستنس Axios شماست

const BASE_URL = '/dashboard/categories/';

export const adminCategoryService = {
  // دریافت لیست کامل
  getAll: async () => {
    const response = await apiClient.get(BASE_URL);
    return response.data;
  },

  // دریافت یک آیتم تکی (برای ویرایش دقیق‌تر اگر نیاز شد)
  getById: async (id) => {
    const response = await apiClient.get(`${BASE_URL}${id}/`);
    return response.data;
  },

  // ایجاد دسته جدید (FormData چون فایل آپلود می‌کنیم)
  create: async (data) => {
    // تبدیل آبجکت به FormData برای هندل کردن تصاویر
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      // فقط مقادیر غیر null را بفرستیم
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    
    const response = await apiClient.post(BASE_URL, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // ویرایش
  update: async (id, data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      // در متد PATCH، اگر عکسی تغییر نکرده باشد، نباید ارسال شود یا باید مدیریت شود
      // اینجا فرض ساده‌سازی است
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });

    const response = await apiClient.patch(`${BASE_URL}${id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // حذف
  delete: async (id) => {
    const response = await apiClient.delete(`${BASE_URL}${id}/`);
    return response.data;
  },
};