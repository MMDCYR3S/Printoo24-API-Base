import apiClient from "../../../api/client";
import { API_ENDPOINTS } from "../../../config/constants";

export const authApi = {
  /**
   * ارسال درخواست ورود به سیستم
   * @param {string} username
   * @param {string} password
   */
  login: async (username, password) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
      username,
      password,
    });
    return response.data;
  },

  /**
   * خروج از سیستم
   * @param {string} refreshToken
   */
  logout: async (refreshToken) => {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
      refresh: refreshToken,
    });
  },

  /**
   * رفرش توکن
   * @param {string} refreshToken
   */
  refreshToken: async (refreshToken) => {
    return apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
      refresh: refreshToken,
    });
  },
};