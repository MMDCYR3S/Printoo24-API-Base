import axios from 'axios';
import toast from 'react-hot-toast';

// 1. تنظیم آدرس پایه (Base URL)
// نکته: در محیط پروداکشن این آدرس از متغیرهای محیطی (.env) خوانده می‌شود
const BASE_URL = 'http://localhost:9010/api/v1'; 

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. Request Interceptor: تزریق خودکار توکن
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

// 3. Response Interceptor: مدیریت خطای 401 و رفرش توکن
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // اگر خطا 401 بود و قبلاً تلاش برای رفرش نکرده بودیم
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            throw new Error('No refresh token');
        }

        // درخواست رفرش توکن طبق سواگر شما
        const response = await axios.post(`${BASE_URL}/accounts/token/refresh/`, {
          refresh: refreshToken,
        });

        // ذخیره توکن جدید (فرض بر این است که سرور اکسس توکن جدید برمی‌گرداند)
        const newAccessToken = response.data.access; 
        localStorage.setItem('accessToken', newAccessToken);

        // آپدیت هدر درخواست قبلی و تکرار آن
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);

      } catch (refreshError) {
        // اگر رفرش هم فایده نداشت، یعنی سشن کلاً منقضی شده
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        toast.error('نشست کاربری شما منقضی شد. لطفاً مجدداً وارد شوید.');
        
        // ریدایرکت به صفحه لاگین (بعداً که روت‌ها را ساختیم دقیق‌تر می‌کنیم)
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // مدیریت سایر خطاها
    if (error.response?.status >= 500) {
        toast.error('خطای سرور. لطفاً بعداً تلاش کنید.');
    }
    
    return Promise.reject(error);
  }
);