// src/app/features/admin/services/adminContactService.js
import { apiClient } from '../../../services/apiClient';

export const adminContactService = {
  getAll: async () => {
    const { data } = await apiClient.get('/dashboard/contacts/');
    return data;
  },

  getById: async (id) => {
    const { data } = await apiClient.get(`/dashboard/contacts/${id}/`);
    return data;
  },

  reply: async ({ id, reply_text }) => {
    const { data } = await apiClient.post(`/dashboard/contacts/${id}/reply/`, { reply_text });
    return data;
  },

  delete: async (id) => {
    await apiClient.delete(`/dashboard/contacts/${id}/`);
    return id; // Return ID for optimistic update
  }
};