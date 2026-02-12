import apiClient from "../../../api/client";
import { API_ENDPOINTS } from "../../../config/constants";

// نکته مهم: حتما باید کلمه export اینجا باشد
export const authApi = { 
  // ورود
  login: async (username, password) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
      username,
      password,
    });
    return response.data;
  },

  // خروج
  logout: async (refreshToken) => {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
      refresh: refreshToken,
    });
  },

  // رفرش
  refreshToken: async (refreshToken) => {
    return apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
      refresh: refreshToken,
    });
  },
};