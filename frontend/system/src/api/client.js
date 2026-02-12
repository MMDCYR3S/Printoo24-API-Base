import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "../config/constants";

// ساخت نمونه اصلی اکسپوس
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 1. Interceptor درخواست: تزریق توکن
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 2. Interceptor پاسخ: مدیریت ارور 401 و رفرش توکن
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // اگر ارور 401 بود و قبلاً یکبار تلاش برای رفرش نکردیم
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem("refreshToken");
        
        if (!refreshToken) {
            throw new Error("No refresh token");
        }

        // درخواست رفرش توکن طبق داکیومنت 
        const response = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.AUTH.REFRESH}`, {
          refresh: refreshToken,
        });

        // ذخیره توکن جدید
        const newAccessToken = response.data.access;
        localStorage.setItem("accessToken", newAccessToken);

        // آپدیت هدر و تکرار درخواست قبلی
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        // اگر رفرش توکن هم منقضی بود، خروج کامل
        console.error("Session expired", refreshError);
        localStorage.clear(); // پاکسازی استوریج
        window.location.href = "/login"; // ریدارکت به لاگین
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;