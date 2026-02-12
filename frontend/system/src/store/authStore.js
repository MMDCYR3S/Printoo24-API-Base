import { create } from "zustand";
import { authApi } from "../features/auth/api/auth";

const useAuthStore = create((set, get) => ({
  user: null,
  accessToken: localStorage.getItem("accessToken") || null,
  refreshToken: localStorage.getItem("refreshToken") || null,
  isAuthenticated: !!localStorage.getItem("accessToken"),
  isLoading: false,
  error: null,

  // اکشن ورود
  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authApi.login(username, password);
      
      // ذخیره در لوکال استوریج
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);

      // آپدیت وضعیت استور
      set({
        user: { username }, // فعلاً یوزرنیم را نگه می‌داریم تا دیتای کامل یوزر بیاید
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        isLoading: false,
      });
      
      return true; // موفقیت
    } catch (error) {
      set({
        error: error.response?.data?.detail || "خطا در ورود به سیستم",
        isLoading: false,
      });
      return false;
    }
  },

  // اکشن خروج امن
  logout: async () => {
    const { refreshToken } = get();
    
    // تلاش برای ارسال به سرور جهت بلک‌لیست شدن 
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch (err) {
        console.warn("Logout API failed, forcing local cleanup", err);
      }
    }

    // پاکسازی کامل مرورگر
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
}));

export default useAuthStore;