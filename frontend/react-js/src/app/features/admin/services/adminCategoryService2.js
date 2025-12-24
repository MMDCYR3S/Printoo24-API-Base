import apiClient from '../../../services/apiClient';

const BASE_URL = '/dashboard/categories/';

export const adminCategoryService2 = {
  getAll: async () => {
    // دریافت لیست دسته‌بندی‌ها (شامل id و name)
    const { data } = await apiClient.get(BASE_URL);
    return data;
  }
};