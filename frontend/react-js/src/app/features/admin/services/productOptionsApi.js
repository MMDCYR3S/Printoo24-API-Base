// src/app/features/admin/products/services/productOptionsApi.js
// ─────────────────────────────────────────────────────────────
// API layer for Step 2 – Product Options
// اگه مسیر axios instance فرق داره، خط زیر رو عوض کن
// ─────────────────────────────────────────────────────────────
import apiClient from '../../../services/apiClient';

const PRODUCTS_BASE = '/ashboard/products';

/**
 * ─── مرحله ۲: همگام‌سازی ویژگی‌ها ───
 * POST /api/v1/dashboard/products/{id}/options/
 * @param {string|number} productId
 * @param {object} payload  – { options: [...] }
 * @returns {Promise<{ results: [{ product_option_id, source_option_id, status }] }>}
 */
export const syncProductOptions = async (productId, payload) => {
  const { data } = await apiClient.post(`${PRODUCTS_BASE}/${productId}/options/`, payload);
  return data;
};

/**
 * ─── حذف یک ویژگی از محصول ───
 * DELETE /api/v1/dashboard/products/{id}/options/{option_id}/
 */
export const deleteProductOption = async (productId, optionId) => {
  const { data } = await apiClient.delete(`${PRODUCTS_BASE}/${productId}/options/${optionId}/`);
  return data;
};

/**
 * ─── ویرایش تنظیمات یک ویژگی (تکی) + ماتریس قیمت + وابستگی‌ها ───
 * PATCH /api/v1/dashboard/products/{id}/update-option-config/
 * @param {string|number} productId
 * @param {object} payload – { product_option_id, is_required, values: [...] }
 */
export const updateOptionConfig = async (productId, payload) => {
  const { data } = await apiClient.patch(`${PRODUCTS_BASE}/${productId}/update-option-config/`, payload);
  return data;
};

/**
 * ─── لیست ویژگی‌های گلوبال (رنگ، جنس، روکش و ...) ───
 * TODO: اندپوینت واقعی رو جایگزین کن
 * GET /api/v1/dashboard/options/
 */
export const fetchGlobalOptions = async () => {
  const { data } = await apiClient.get('/dashboard/options/');
  return data;
  // Expected shape:
  // [
  //   {
  //     id: 20,
  //     name: "color",
  //     label: "رنگ",
  //     input_type: "radio",
  //     values: [
  //       { id: 301, label: "سفید" },
  //       { id: 302, label: "مشکی" },
  //     ]
  //   },
  //   ...
  // ]
};

/**
 * ─── لیست تیراژها (quantity tiers) ───
 * TODO: اندپوینت واقعی رو جایگزین کن
 * GET /api/v1/dashboard/quantities/
 */
export const fetchQuantityTiers = async () => {
  const { data } = await apiClient.get('/dashboard/quantities/');
  return data;
  // Expected shape:
  // [
  //   { id: 1, label: "۱۰۰ عدد" },
  //   { id: 2, label: "۲۰۰ عدد" },
  //   { id: 10, label: "۱,۰۰۰ عدد" },
  //   ...
  // ]
};