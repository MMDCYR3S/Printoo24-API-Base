import { apiClient } from '../../../services/apiClient';

export const adminDashboardService = {
  getAllStats: async () => {
    const { data } = await apiClient.get('/dashboard/stats/');
    return data;
  },
};