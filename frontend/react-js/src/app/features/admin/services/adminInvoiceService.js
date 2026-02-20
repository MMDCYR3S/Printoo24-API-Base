import { apiClient } from '../../../services/apiClient';

const BASE_URL = '/dashboard/invoices/';

export const adminInvoiceService = {
  // دریافت فاکتور بر اساس آیدی سفارش
  getByOrderId: async (orderId) => {
    const { data } = await apiClient.get(`${BASE_URL}by-order/${orderId}/`);
    return data;
  },

  // ایجاد فاکتور جدید
  create: async (data) => {
    const { data: response } = await apiClient.post(BASE_URL, data);
    return response;
  },

  // ویرایش فاکتور
  update: async (id, data) => {
    const { data: response } = await apiClient.patch(`${BASE_URL}${id}/`, data);
    return response;
  },

  // حذف فاکتور
  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  // نهایی‌سازی فاکتور
  approve: async (id) => {
    const { data } = await apiClient.patch(`${BASE_URL}${id}/approve/`);
    return data;
  },

  // تغییر وضعیت دستی (PENDING, PAID_FULL, etc.)
  changeStatus: async (id, status) => {
    const { data } = await apiClient.patch(`${BASE_URL}${id}/status/`, { status });
    return data;
  }
};