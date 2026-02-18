import api from "@/api/client";

export const designService = {
  // دریافت لیست سفارشات کارتابل طراح
  getOrders: async () => {
    const response = await api.get("/operations/order/list/");
    return response.data;
  },

  // دریافت جزئیات کامل برای طراح
  getOrderDetail: async (id) => {
    const response = await api.get(`/operations/order/detail/${id}/`);
    return response.data;
  },

  // تایید و ارسال به مرحله بعد
  approveOrder: async (id) => {
    return await api.post(`/operations/orders/${id}/approve/`);
  },

  // رد سفارش با ذکر دلیل
  rejectOrder: async (id, description) => {
    return await api.post(`/operations/orders/${id}/reject/`, { description });
  }
};