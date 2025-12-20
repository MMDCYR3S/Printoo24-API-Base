import { apiClient } from '../../../services/apiClient';

const BASE_URL = '/dashboard/orders/';

export const adminOrderService = {
  // دریافت لیست کل سفارشات
  getAll: async () => {
    const response = await apiClient.get(BASE_URL);
    return response.data;
  },

  // دریافت جزئیات یک سفارش
  getById: async (id) => {
    const response = await apiClient.get(`${BASE_URL}${id}/`);
    return response.data;
  },

  // ایجاد سفارش دستی (پیچیده است، بعداً فرمش را می‌سازیم)
  create: async (data) => {
    const response = await apiClient.post(BASE_URL, data);
    return response.data;
  },

  // آپدیت پارشیال (مثلاً تغییر آدرس یا نوع)
  update: async (id, data) => {
    const response = await apiClient.patch(`${BASE_URL}${id}/`, data);
    return response.data;
  },

  // حذف تکی
  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
  },

  // حذف گروهی (API خاصی که دادی)
  bulkDelete: async (ids) => {
    // طبق داکیومنت، آرایه ids باید در بادی ارسال شود
    await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: { ids } });
  },

  // حذف یک آیتم خاص از داخل سفارش (مثلاً حذف کارت ویزیت از سفارش کل)
  deleteItem: async (orderId, itemId) => {
    await apiClient.delete(`${BASE_URL}${orderId}/items/${itemId}/`);
  },
};