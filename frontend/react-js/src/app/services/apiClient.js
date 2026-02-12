// src/app/services/apiClient.js
import axios from 'axios';

// مطمئن شو که پورت درسته
const BASE_URL = '/api/v1';

// فانکشن کمکی برای تولید شناسه مهمان (بدون تغییر در ساختار اصلی)
const getGuestToken = () => {
  let token = localStorage.getItem('guest_token');
  if (!token) {
    token = 'guest_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('guest_token', token);
  }
  return token;
};

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      // فقط زمانی که توکن لاگین نداریم، توکن مهمان را بفرست
      config.headers['X-Guest-Token'] = getGuestToken();
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // اگر ۴۰۱ بود و بار اوله
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw new Error('No refresh token');

        const response = await axios.post(`${BASE_URL}/accounts/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = response.data.access || response.data.tokens?.access;

        if (newAccessToken) {
          localStorage.setItem('accessToken', newAccessToken);
          originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
          // ریکوئست رو دوباره میفرسته
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // اگه رفرش هم نشد، یعنی واقعا باید بره بیرون
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;