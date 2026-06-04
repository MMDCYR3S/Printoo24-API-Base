import { apiClient } from '../../../services/apiClient';

const BASE_URL = '/dashboard/expenses';

export const expenseService = {
  // لیست همه هزینه‌ها
  getAll: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/`);
    return data;
  },

  // هزینه‌های یک سفارش خاص
  getByOrder: async (orderId) => {
    const { data } = await apiClient.get(`${BASE_URL}/by-order/${orderId}/`);
    return data;
  },

  // آمار کلی هزینه‌ها و سود
  getStatistics: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/statistics/`);
    return data;
  },

  // لیست سفارشات دارای فاکتور قفل‌نشده (برای dropdown)
  getUnlockedInvoices: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/unlocked-invoices/`);
    return data;
  },

  // ایجاد هزینه جدید
  create: async (payload) => {
    // payload: { name, amount, order? }
    const { data } = await apiClient.post(`${BASE_URL}/`, payload);
    return data;
  },

  // ویرایش کامل
  update: async (id, payload) => {
    const { data } = await apiClient.put(`${BASE_URL}/${id}/`, payload);
    return data;
  },

  // ویرایش جزئی
  patch: async (id, payload) => {
    const { data } = await apiClient.patch(`${BASE_URL}/${id}/`, payload);
    return data;
  },

  // حذف
  remove: async (id) => {
    await apiClient.delete(`${BASE_URL}/${id}/`);
  },
};