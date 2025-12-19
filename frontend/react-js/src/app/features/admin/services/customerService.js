// src/app/features/admin/customers/services/customerService.js
import apiClient from '../../../services/apiClient'; // فرض بر وجود اینستنس axios

const ENDPOINT = '/dashboard/customers/';

export const customerService = {
  // دریافت لیست
  getAll: async (params) => {
    // اگر سرور از کوئری پارامتر پشتیبانی نکند، کلاینت ساید هندل میکنیم
    // اما استاندارد این است که ارسال کنیم
    const { data } = await apiClient.get(ENDPOINT, { params });
    return data;
  },

  // دریافت یک مورد
  getById: async (id) => {
    const { data } = await apiClient.get(`${ENDPOINT}${id}/`);
    return data;
  },

  // ایجاد
  create: async (payload) => {
    const { data } = await apiClient.post(ENDPOINT, payload);
    return data;
  },

  // ویرایش
  update: async (id, payload) => {
    const { data } = await apiClient.put(`${ENDPOINT}${id}/`, payload);
    return data;
  },

  // حذف تکی
  delete: async (id) => {
    await apiClient.delete(`${ENDPOINT}${id}/`);
    return id;
  },

  // حذف گروهی
  bulkDelete: async (ids) => {
    // معمولاً لیست آیدی‌ها در بادی ارسال می‌شود
    await apiClient.delete(`${ENDPOINT}bulk-delete/`, { data: { ids } });
    return ids;
  },

  // تغییر وضعیت گروهی
  bulkStatus: async ({ ids, active }) => {
    await apiClient.patch(`${ENDPOINT}bulk-status/`, { ids }, {
      params: { active } // طبق داکیومنت active به عنوان کوئری است
    });
    return { ids, active };
  },
};