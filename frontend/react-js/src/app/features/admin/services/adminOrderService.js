import { apiClient } from '../../../services/apiClient';

const BASE_URL = '/dashboard/orders/';

export const adminOrderService = {
  // ۱. دریافت لیست سفارشات (با پشتیبانی از پارامترهای سرورساید مثل page, search, status_id)
  getAll: async (params = {}) => {
    const response = await apiClient.get(BASE_URL, { params });
    return response.data;
  },

  // ۲. دریافت جزئیات یک سفارش
  getById: async (id) => {
    const response = await apiClient.get(`${BASE_URL}${id}/`);
    return response.data;
  },

  // ۳. ایجاد سفارش دستی (پشتیبانی از total_price دلخواه)
  create: async (data) => {
    const response = await apiClient.post(BASE_URL, data);
    return response.data;
  },

  // ۴. ویرایش اطلاعات کلی سفارش (مثل تغییر type یا total_price)
  update: async (id, data) => {
    const response = await apiClient.patch(`${BASE_URL}${id}/`, data);
    return response.data;
  },

  // ۵. تغییر وضعیت سفارش (متد جدید طبق API)
  changeStatus: async (id, data) => {
    // data باید شامل { status_code, description } باشد
    const response = await apiClient.post(`${BASE_URL}${id}/change-status/`, data);
    return response.data;
  },

  // ۶. حذف تکی
  delete: async (id) => {
    const response = await apiClient.delete(`${BASE_URL}${id}/`);
    return response.data;
  },

  // ۷. حذف گروهی
  bulkDelete: async (ids) => {
    const response = await apiClient.delete(`${BASE_URL}bulk-delete/`, { data: { ids } });
    return response.data;
  },

  // ۸. حذف یک آیتم خاص از داخل سفارش
  deleteItem: async (orderId, itemId) => {
    const response = await apiClient.delete(`${BASE_URL}${orderId}/items/${itemId}/`);
    return response.data;
  },

  // ۹. آپلود فایل برای یک آیتم از سفارش (متد جدید)
  uploadItemFile: async (orderId, itemId, formData) => {
    const response = await apiClient.post(`${BASE_URL}${orderId}/items/${itemId}/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // ۱۰. دریافت لیست وضعیت‌های سیستم (متد جدید)
  getStatuses: async () => {
    const response = await apiClient.get(`${BASE_URL}statuses/`);
    return response.data;
  },
   
};