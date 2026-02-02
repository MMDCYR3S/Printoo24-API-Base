import { apiClient } from '../../../services/apiClient';

const BASE_URL = '/dashboard';

export const adminDashboardService = {
  // 1. آمار سفارشات
  getOrderStats: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/order-stats/`);
    return data;
  },

  // 2. آمار محصولات
  getProductStats: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/product-stats/`);
    return data;
  },

  // 3. آمار مالی (نمودار فروش)
  getFinancialStats: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/stats/financial/`);
    return data;
  },

  // 4. آمار کاربران
  getUserStats: async () => {
    const { data } = await apiClient.get(`${BASE_URL}/user-stats/`);
    return data;
  },
};