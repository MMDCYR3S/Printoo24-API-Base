// src/app/features/admin/products/services/adminProductService.js
import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/products/';

export const adminProductService = {
  // دریافت همه محصولات
  getAll: async () => {
    const { data } = await apiClient.get(BASE_URL);
    return data;
  },

  // حذف تکی (اگر نیاز شد)
  delete: async (id) => {
    await apiClient.delete(`${BASE_URL}${id}/`);
    return id;
  },

  // حذف گروهی (Bulk Delete)
  bulkDelete: async (product_ids) => {
    // نکته امنیتی و فنی: در axios برای متد delete باید body را در data بفرستیم
    const response = await apiClient.delete(`${BASE_URL}bulk-delete/`, {
      data: product_ids // طبق داکیومنت آرایه مستقیم یا آبجکت
    });
    return response.data;
  },

  // تغییر وضعیت گروهی (Bulk Status)
  bulkStatus: async ({ product_ids, is_active }) => {
    const response = await apiClient.patch(`${BASE_URL}bulk-status/`, {
      product_ids,
      is_active
    });
    return response.data;
  },
};