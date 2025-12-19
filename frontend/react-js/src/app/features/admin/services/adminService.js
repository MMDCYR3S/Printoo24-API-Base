// src/app/services/adminService.js
import apiClient from '../../../services/apiClient'; // فرض بر این است که اینستنس axios شماست

export const adminService = {
  getAllProducts: async () => {
    const { data } = await apiClient.get('/dashboard/products/');
    return data;
  },
  // متدهای بعدی مثل delete یا update اینجا اضافه می‌شوند
};