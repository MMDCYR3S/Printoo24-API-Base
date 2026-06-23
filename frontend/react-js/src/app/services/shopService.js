// src/app/services/shopService.js
import { apiClient } from './apiClient';

export const shopService = {
  // دریافت لیست محصولات
  getProducts: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.categories) {
      filters.categories.forEach(cat => params.append('category', cat));
    }
    if (filters.search) params.append('search', filters.search);
    const response = await apiClient.get('/shop/grid/', { params });
    return response.data;
  },

  // دریافت جزئیات محصول
  getProductDetail: async (slug) => {
    const response = await apiClient.get(`/shop/detail/${slug}/`);
    return response.data;
  },


  calculateLivePrice: async (productId, selections) => {
    const response = await apiClient.post(`/shop/products/${productId}/calculate-price/`, {
      selections: selections
    });
    return response.data;
  },

  // جستجوی محصولات
  // طبق مستندات: GET /api/v1/shop/search/?q=<keyword>
  // این اندپوینت داخل name, description, options جستجو می‌کند و مستقیماً آرایه برمی‌گرداند.
  searchProducts: async (query, page = 1) => {
    const params = new URLSearchParams();
    params.append('q', query);
    // این اندپوینت pagination ندارد → صفحه‌بندی نادیده گرفته می‌شود
    const response = await apiClient.get('/shop/search/', { params });
    // پاسخ مستقیماً آرایه است
    return Array.isArray(response.data) ? response.data : [];
  },

  // ──────────────────────────────────────────────────────────────────────────
  //  قابلیت‌های ادمین — ثبت سفارش دستی برای مشتری
  //  توجه: این متدها فقط زمانی فراخوانی می‌شوند که کاربر is_superuser === true باشد
  // ──────────────────────────────────────────────────────────────────────────

  /**
   * دریافت لیست مشتریان برای سفارش دستی (فقط ادمین)
   * GET /api/v1/dashboard/orders/customers/
   *
   * پاسخ: آرایه‌ای از مشتریان غیرادمین به همراه addresses هرکدام
   */
  getDashboardCustomers: async () => {
    const response = await apiClient.get('/dashboard/orders/customers/');
    return response.data;
  },

  /**
   * ثبت سفارش دستی برای یک مشتری (فقط ادمین)
   * POST /api/v1/dashboard/orders/
   *
   * @param {Object} payload
   * @param {number} payload.user_id           آیدی مشتری انتخاب‌شده
   * @param {number} payload.address_id        آیدی آدرس انتخاب‌شده از لیست آدرس‌های مشتری
   * @param {string} payload.type              نوع سفارش (مثلاً "1")
   * @param {number} payload.product_id        آیدی محصول
   * @param {boolean} payload.has_design       آیا فایل طراحی آپلود می‌شود؟
   * @param {Array<{field_id:number, choice_id:number}>} payload.selected_options
   *
   * توجه: company_name هرگز در پیلود ارسال نمی‌شود
   */
  createManualOrder: async (payload) => {
    const response = await apiClient.post('/dashboard/orders/', payload);
    return response.data;
  },
};
