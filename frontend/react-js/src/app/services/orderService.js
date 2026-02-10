import { apiClient } from './apiClient';

export const orderService = {
  // دریافت لیست آدرس‌های ثبت شده کاربر
  getAddresses: async () => {
    const response = await apiClient.get('/order/addresses/');
    return response.data;
  },

  // ثبت سفارش گروهی (Checkout All)
  checkout: async (payload) => {
    const response = await apiClient.post('/order/checkout/all/', payload);
    return response.data;
  }
};