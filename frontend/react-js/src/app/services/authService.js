import { apiClient } from './apiClient';

export const authService = {
  // 🔐 ورود کاربر
  login: async (credentials) => {
    // credentials: { username, password }
    const response = await apiClient.post('/accounts/login/', credentials);
    return response.data;
  },

  // 📝 ثبت نام (با اینکه در سواگر بادی مشخص نبود، معمولا یوزرنیم/ایمیل/پسورد است)
  register: async (userData) => {
    const response = await apiClient.post('/accounts/register/', userData);
    return response.data;
  },

  // ✅ تایید کد (Verify)
  verifyEmail: async (data) => {
    // data: { email, code }
    const response = await apiClient.post('/accounts/verify/', data);
    return response.data;
  },

  // 🚪 خروج (ارسال رفرش توکن به لیست سیاه)
  logout: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    // طبق سواگر برای خروج باید رفرش توکن ارسال شود
    await apiClient.post('/accounts/logout/', { refresh: refreshToken });
    
    // پاکسازی کلاینت
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },

  // 🔄 فراموشی رمز عبور (درخواست)
  requestPasswordReset: async (email) => {
    return await apiClient.post('/accounts/password/reset/', { email });
  },

  // 🔄 تایید رمز عبور جدید
  confirmPasswordReset: async (uidb64, token, passwords) => {
    // passwords: { password, password_confirm }
    return await apiClient.post(
      `/accounts/password/reset/confirm/${uidb64}/${token}/`, 
      passwords
    );
  }
};