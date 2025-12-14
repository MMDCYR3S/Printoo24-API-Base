// src/app/services/modalService.js
import { apiClient } from './apiClient';

export const modalService = {
  // دریافت مودال فعال
  getActiveModal: async () => {
    // GET /api/v1/dashboard/modals/active/
    const response = await apiClient.get('/dashboard/modals/active/');
    return response.data;
  },
};