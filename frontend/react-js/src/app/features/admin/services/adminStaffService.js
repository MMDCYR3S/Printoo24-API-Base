import apiClient from '../../../services/apiClient'; // آدرس ایمپورت رو چک کن، اگه تو همون پوشه services هست همین درسته

const ENDPOINT = '/dashboard/staffs/';

export const adminStaffService = {
  // دریافت لیست کارمندان
  getAll: async () => {
    const { data } = await apiClient.get(ENDPOINT);
    return data;
  },

  // دریافت لیست نقش‌ها
  getRoles: async () => {
    const { data } = await apiClient.get(`${ENDPOINT}roles/`);
    return data;
  },

  // ایجاد کارمند جدید
  create: async (payload) => {
    const { data } = await apiClient.post(ENDPOINT, payload);
    return data;
  },

  // دریافت جزئیات یک کارمند (اگه نیاز شد)
  getById: async (id) => {
    const { data } = await apiClient.get(`${ENDPOINT}${id}/`);
    return data;
  },

  // ویرایش کارمند (نقش و وضعیت)
  update: async (id, payload) => {
    const { data } = await apiClient.patch(`${ENDPOINT}${id}/`, payload);
    return data;
  },

  // حذف تکی
  delete: async (id) => {
    await apiClient.delete(`${ENDPOINT}${id}/`);
    return id;
  },

  // تغییر نقش گروهی
  bulkChangeRole: async (payload) => {
    const { data } = await apiClient.post(`${ENDPOINT}bulk-change-role/`, payload);
    return data;
  },

  // فعال/غیرفعال‌سازی گروهی
  bulkToggleStatus: async (payload) => {
    const { data } = await apiClient.post(`${ENDPOINT}bulk-toggle-status/`, payload);
    return data;
  },

  // حذف گروهی
  bulkDelete: async (userIds) => {
    // طبق مستنداتی که دادی
    const { data } = await apiClient.delete(`${ENDPOINT}bulk-delete/`, { data: { user_ids: userIds } });
    return data;
  }
};