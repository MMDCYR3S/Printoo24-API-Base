import { apiClient } from './apiClient';

export const contactService = {
  // ارسال پیام تماس با ما
  sendMessage: async (data) => {
    // POST /api/v1/dashboard/contacts/
    const response = await apiClient.post('/dashboard/contacts/', data);
    return response.data;
  },
};