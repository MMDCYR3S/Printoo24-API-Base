// src/app/services/authService.js
import { apiClient } from './apiClient';

export const authService = {
  // 🔐 ورود کاربر
  login: async (credentials) => {
    // POST /api/v1/accounts/login/
    const response = await apiClient.post('/accounts/auth/', credentials);
    return response.data; // این دیتا شامل { user: {...}, tokens: {...} } هست
  },

  // 📝 ثبت نام
  register: async (userData) => {
    // POST /api/v1/accounts/register/
    const response = await apiClient.post('/accounts/register/', userData);
    return response.data;
  },

  // ✅ تایید ایمیل/کد
  verifyEmail: async (data) => {
    // POST /api/v1/accounts/verify/
    const response = await apiClient.post('/accounts/verify/', data);
    return response.data;
  },

  // 🚪 خروج
  logout: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      // POST /api/v1/accounts/logout/
      await apiClient.post('/accounts/logout/', { refresh: refreshToken });
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },
  
  // رفرش توکن (این معمولا توی اینترسپتور استفاده میشه ولی اینجا هم باشه خوبه)
  refreshToken: async (refresh) => {
      // POST /api/v1/accounts/token/refresh/
      const response = await apiClient.post('/accounts/token/refresh/', { refresh });
      return response.data;
  }
};