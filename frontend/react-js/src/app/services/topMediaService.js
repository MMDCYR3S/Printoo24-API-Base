// src/app/services/topMediaService.js
import { apiClient } from './apiClient';

/**
 * سرویس دریافت رسانه بالای هدر (عکس / گیف فعال)
 * طبق مستندات: GET /api/v1/home/site-media/
 * این اندپوینت نیازی به توکن ندارد و مستقیماً رسانه فعال را برمی‌گرداند.
 *
 * ساختار پاسخ:
 * {
 *   id: number,
 *   file_url: string,
 *   is_active: boolean,
 *   created_at: string,
 *   updated_at: string
 * }
 */
export const topMediaService = {
  getActiveMedia: async () => {
    const response = await apiClient.get('/home/site-media/');
    return response.data;
  },
};
