// src/app/services/homeService.js
import { apiClient } from './apiClient';

export const homeService = {
  // دریافت لیست اسلایدرها
  getSliders: async () => {
    // طبق مستندات: GET /api/v1/home/sliders/
    const response = await apiClient.get('/home/sliders/');
    return response.data;
  },

  // دریافت مودال فعال صفحه اصلی
  // طبق مستندات: GET /api/v1/home/modals/
  // این متد تنها یک آبجکت برمی‌گرداند (آخرین مودالی که is_active=True باشد).
  // اگر هیچ مودال فعالی نباشد، پاسخ 200 OK با مقدار null یا دیکشنری خالی برمی‌گردد.
  // فرانت باید چک کند که آیا دیتایی دریافت کرده یا خیر.
  getActiveModal: async () => {
    const response = await apiClient.get('/home/modals/');
    // ممکن است null یا {} برگردد → در کامپوننت چک می‌شود
    return response.data;
  },
};
