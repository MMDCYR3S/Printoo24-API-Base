// src/app/features/admin/services/adminContactService.js
import { apiClient } from '../../../services/apiClient';

export const adminContactService = {
  // دریافت لیست تمام پیام‌ها
  getAll: async () => {
    const { data } = await apiClient.get('/dashboard/contacts/');
    return data;
  },

  // دریافت جزئیات یک پیام (اگر نیاز شد، فعلا لیست کامل دیتا را دارد)
  getById: async (id) => {
    const { data } = await apiClient.get(`/dashboard/contacts/${id}/`);
    return data;
  },

  // پاسخ به پیام
  reply: async ({ id, reply_text }) => {
    // طبق داکیومنت بادی باید جیسون باشد
    const { data } = await apiClient.post(`/dashboard/contacts/${id}/reply/`, { reply_text });
    return data;
  },
};