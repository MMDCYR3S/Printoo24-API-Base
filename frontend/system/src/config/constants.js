// src/config/constants.js

// آدرس پایه طبق داکیومنت (قابل تغییر برای پروداکشن)
export const API_BASE_URL = "http://127.0.0.1:8000/api/v1"; 

// وضعیت‌های سفارش [cite: 157, 160, 162, 166]
export const ORDER_STATUS = Object.freeze({
  PENDING_ADMIN: "PENDING_PROGRESS_ADMIN", // در انتظار بررسی ادمین
  PENDING_DESIGN: "PENDING_PROJECT",       // در انتظار طراحی
  IN_PRINT: "PROGRESS_PRINT",              // در حال چاپ
  DELIVERED: "RECEIVED",                   // تحویل شده
});

// اندپوینت‌ها دقیقاً طبق داکیومنت PDF
export const API_ENDPOINTS = Object.freeze({
  AUTH: {
    LOGIN: "/users/auth/login/",           // [cite: 11]
    LOGOUT: "/users/auth/logout/",         // [cite: 12] با رفرش توکن
    REFRESH: "/users/auth/refresh/",       // 
  },
  ORDERS: {
    LIST: "/operations/order/list/",       // [cite: 89]
    CREATE: "/order/",                     // [cite: 37]
    // دریافت جزئیات یک سفارش خاص
    DETAIL: (id) => `/operations/order/detail/${id}/`, // [cite: 89]
    // تایید وضعیت توسط پرسنل (طراح/چاپ)
    APPROVE: (id) => `/operations/orders/${id}/approve/`, // [cite: 172]
    // تغییر وضعیت دستی توسط ادمین
    TRANSITION: (id) => `/operations/transition/${id}/`, // [cite: 130]
  },
  COSTS: {
    TYPES: "/operations/costs-types/",     // [cite: 193]
    SUBMIT: (id) => `/operations/orders/${id}/costs/submit/`, // [cite: 193]
    REPORTS: "/financial/costs/reports/",  // [cite: 297]
    APPROVE_REPORT: (id) => `/financial/costs/reports/${id}/decide/`, // [cite: 297]
  },
  SHIPMENT: {
    LIST: "/logistics/shipments/",         // [cite: 249]
    // تایید نهایی و ارسال به مشتری
    APPROVE: (id) => `/logistics/shipments/${id}/approve-status/`, // [cite: 260]
  }
});