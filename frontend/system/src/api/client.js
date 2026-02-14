import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "../config/constants";

// ساخت نمونه اصلی اکسپوس
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// 1. Interceptor درخواست: تزریق توکن + اصلاح آدرس
apiClient.interceptors.request.use(
  (config) => {
    // الف) تزریق توکن احراز هویت
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // ب) اصلاح خودکار آدرس (Auto-Prefix Fix)
    // اگر آدرس با /api/v1 شروع نشده بود و لینک کامل (http) هم نبود، پیشوند را اضافه کن
    if (config.url && !config.url.startsWith("/api/v1") && !config.url.startsWith("http")) {
      // حذف اسلش اول اگر وجود داشته باشد تا دو تا اسلش نشود
      const cleanUrl = config.url.startsWith("/") ? config.url : `/${config.url}`;
      config.url = `/api/v1${cleanUrl}`;
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

        // درخواست رفرش توکن (چون این آدرس در constants ثابت است، پیشوند دارد و مشکلی نیست)
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
        console.error("Session expired", refreshError);
        localStorage.clear();
        window.location.href = "/auth/login"; 
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;