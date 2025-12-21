import { apiClient } from '../../../services/apiClient';

// --- Provinces ---
const PROVINCE_URL = '/dashboard/provinces/';

export const adminProvinceService = {
  getAll: async () => {
    const { data } = await apiClient.get(PROVINCE_URL);
    return data;
  },
  create: async (payload) => {
    const { data } = await apiClient.post(PROVINCE_URL, payload);
    return data;
  },
  update: async ({ id, data }) => {
    const { data: response } = await apiClient.put(`${PROVINCE_URL}${id}/`, data);
    return response;
  },
  delete: async (id) => {
    await apiClient.delete(`${PROVINCE_URL}${id}/`);
  },
  bulkDelete: async (ids) => {
    await apiClient.post(`${PROVINCE_URL}bulk-delete/`, { ids });
  },
};

// --- Cities ---
const CITY_URL = '/dashboard/cities/';

export const adminCityService = {
  getAll: async (provinceId = null) => {
    const params = {};
    // فقط اگر استان انتخاب شده بود ارسالش می‌کنیم
    if (provinceId && provinceId !== 'all') {
      params.province_id = provinceId;
    }
    const { data } = await apiClient.get(CITY_URL, { params });
    return data;
  },
  create: async (payload) => {
    const { data } = await apiClient.post(CITY_URL, payload);
    return data;
  },
  update: async ({ id, data }) => {
    const { data: response } = await apiClient.put(`${CITY_URL}${id}/`, data);
    return response;
  },
  delete: async (id) => {
    await apiClient.delete(`${CITY_URL}${id}/`);
  },
  bulkDelete: async (ids) => {
    await apiClient.post(`${CITY_URL}bulk-delete/`, { ids });
  },
};