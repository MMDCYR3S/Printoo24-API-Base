import { create } from "zustand";
import { authApi } from "../features/auth/api/authService";

const useAuthStore = create((set, get) => ({
  // وضعیت اولیه از LocalStorage خوانده می‌شود تا با رفرش صفحه دیتا نپرد
  user: JSON.parse(localStorage.getItem("user")) || null,
  accessToken: localStorage.getItem("accessToken") || null,
  refreshToken: localStorage.getItem("refreshToken") || null,
  isAuthenticated: !!localStorage.getItem("accessToken"),
  isLoading: false,

  // --- اکشن‌ها ---

  login: async (username, password) => {
    set({ isLoading: true });
    try {
      const data = await authApi.login(username, password);

      // فرض بر این است که بک‌ند آبجکت user را همراه توکن‌ها برمی‌گرداند.
      // اگر بک‌ند این کار را نمی‌کند، اینجا باید یک ریکوئست جداگانه به /profile زده شود.
      const user = data.user || { username, role_name: "کاربر سیستم" }; 

      // ذخیره‌سازی در LocalStorage
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("user", JSON.stringify(user));

      // آپدیت وضعیت برنامه
      set({
        user: user,
        accessToken: data.access,
        refreshToken: data.refresh,
        isAuthenticated: true,
        isLoading: false,
      });

      return true; // لاگین موفق
    } catch (error) {
      console.error("Login failed:", error);
      set({ isLoading: false });
      return false; // لاگین ناموفق
    }
  },

  logout: async () => {
    const { refreshToken } = get();

    // 1. تلاش برای لاگ‌اوت سمت سرور (Best Effort)
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken);
      } catch (err) {
        console.warn("Server logout warning:", err.message);
      }
    }

    // 2. پاکسازی سمت کلاینت (همیشه انجام شود)
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