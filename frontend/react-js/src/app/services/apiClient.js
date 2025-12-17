// src/app/services/apiClient.js
import axios from 'axios';
import toast from 'react-hot-toast';

// ⚠️ آدرس پورت رو مطابق سرور خودت بذار (مثلا 9010)
const BASE_URL = 'http://localhost:9010/api/v1'; 

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
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // خطای 401 یعنی توکن اکسپایر شده
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw new Error('No refresh token');

        // ⚠️ آدرس طبق سواگر شما: /accounts/token/refresh/
        const response = await axios.post(`${BASE_URL}/accounts/token/refresh/`, {
          refresh: refreshToken,
        });

        // معمولا بک‌اند اینجا { "access": "..." } برمی‌گردونه
        // اما اگه مثل لاگین { tokens: ... } برگردوند باید چک کنی
        // فرض بر استاندارد SimpleJWT:
        const newAccessToken = response.data.access || response.data.tokens?.access; 
        
        localStorage.setItem('accessToken', newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        // هدایت به لاگین
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);