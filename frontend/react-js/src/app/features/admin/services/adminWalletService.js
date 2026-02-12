import apiClient from '../../../services/apiClient';

// نکته: مطمئن شو که Base URL توی apiClient ست شده باشه (مثلا /api/v1)
// آدرس نهایی باید بشه: /api/v1/dashboard/wallets/adjust-balance/

const ENDPOINT = '/dashboard/wallets/';

export const adminWalletService = {
  getAll: async () => {
    const { data } = await apiClient.get(ENDPOINT);
    return data;
  },

  adjustBalance: async (payload) => {
    // تغییر: اطمینان از وجود اسلش در آخر آدرس
    const { data } = await apiClient.post(`${ENDPOINT}adjust-balance/`, payload);
    return data;
  },

  getTransactions: async (id) => {
    const { data } = await apiClient.get(`${ENDPOINT}${id}/transactions/`);
    return data;
  }
};