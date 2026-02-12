// src/config/constants.js

// 1. آدرس پایه فقط شامل پورت و هاست باشد (بدون /api/v1)
export const API_BASE_URL = "http://localhost:8010"; 

export const API_ENDPOINTS = {
  AUTH: {
    // دقیقاً طبق تصویر Swagger شما:
    LOGIN: "/api/v1/users/auth/login/",
    LOGOUT: "/api/v1/users/auth/logout/",
    REFRESH: "/api/v1/users/auth/refresh/",
  },
  
  ORDERS: {
    // طبق الگوی جدید:
    LIST: "/api/v1/operations/order/list/",
    CREATE: "/api/v1/order/",
    DETAIL: (id) => `/api/v1/operations/order/detail/${id}/`,
    APPROVE: (id) => `/api/v1/operations/orders/${id}/approve/`,
    TRANSITION: (id) => `/api/v1/operations/transition/${id}/`,
  },
  
  COSTS: {
    TYPES: "/api/v1/operations/costs-types/",
    SUBMIT: (id) => `/api/v1/operations/orders/${id}/costs/submit/`,
    REPORTS: "/api/v1/financial/costs/reports/",
    APPROVE_REPORT: (id) => `/api/v1/financial/costs/reports/${id}/decide/`,
  },
  
  SHIPMENT: {
    LIST: "/api/v1/logistics/shipments/",
    APPROVE: (id) => `/api/v1/logistics/shipments/${id}/approve-status/`,
  }
};

// وضعیت‌های سفارش (ثابت می‌مانند)
export const ORDER_STATUS = Object.freeze({
  PENDING_ADMIN: "PENDING_PROGRESS_ADMIN",
  PENDING_DESIGN: "PENDING_PROJECT",
  IN_PRINT: "PROGRESS_PRINT",
  DELIVERED: "RECEIVED",
});