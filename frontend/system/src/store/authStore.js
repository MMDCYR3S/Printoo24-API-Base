import { create } from "zustand";
import { authApi } from "../features/auth/api/authService";

const useAuthStore = create((set, get) => ({
  user: JSON.parse(localStorage.getItem("user")) || null,
  accessToken: localStorage.getItem("accessToken") || null,
  refreshToken: localStorage.getItem("refreshToken") || null,
  isAuthenticated: !!localStorage.getItem("accessToken"),
  isLoading: false,

  // اکشن ورود
  login: async (username, password) => {
    set({ isLoading: true });
    try {
      const data = await authApi.login(username, password);
      
      // ذخیره در LocalStorage برای پایداری بعد از رفرش صفحه
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      set({
        user: data.user,
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        isLoading: false,
      });
      return true; // موفقیت
    } catch (error) {
      console.error("Login failed:", error);
      set({ isLoading: false });
      return false; // شکست
    }
  },

  // اکشن خروج
  logout: async () => {
    const { refreshToken } = get();
    
    // تلاش برای بلک‌لیست کردن توکن در سمت سرور
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch (err) {
        console.warn("Server logout failed (token might be expired), clearing local data anyway.");
      }
    }

    // پاکسازی کامل
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");
    
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },
}));

export default useAuthStore;