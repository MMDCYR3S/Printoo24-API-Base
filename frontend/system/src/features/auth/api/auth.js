import apiClient from "../../../api/client"; // کلاینت که ساختیم
import { API_ENDPOINTS } from "../../../config/constants"; // آدرس‌ها

export const authApi = {
  // ورود کاربر [cite: 11]
  login: async (username, password) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
      username,
      password,
    });
    return response.data;
  },

  // خروج امن (لیست سیاه کردن توکن) [cite: 22, 24]
  logout: async (refreshToken) => {
    // طبق داکیومنت، رفرش توکن باید در بادی ارسال شود
    return apiClient.post(API_ENDPOINTS.AUTH.LOGOUT, {
      refresh: refreshToken, 
    });
  },

  // رفرش توکن (توسط اینترسپتور استفاده می‌شود ولی اینجا هم تعریف می‌کنیم)
  refreshToken: async (refresh) => {
    return apiClient.post(API_ENDPOINTS.AUTH.REFRESH, { refresh });
  },
};