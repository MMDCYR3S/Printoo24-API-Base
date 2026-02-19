import api from "@/api/client";

// نگاشت کننده (Mapper) برای تبدیل فرمت فرم به فرمت بک‌ند
const mapOrderToApiPayload = (data) => {
  return {
    user_id: data.user_id,
    address_id: data.address_id,
    description: data.description,
    price: data.price, // قیمت کل
    items: data.items.map((item) => ({
      product_slug: item.product_name, // طبق توافق: نام محصول به عنوان اسلاگ میره
      quantity: item.quantity,
      selections: {
        custom_width: item.width || 0,
        custom_height: item.height || 0,
        description: item.description || "",
      },
    })),
  };
};

export const orderService = {
  getAllOrders: async (params) => {
    const response = await api.get("/order/", { params });
    return response.data;
  },

  getOrderById: async (id) => {
    const response = await api.get(`/order/${id}/`);
    return response.data;
  },

  // متد جدید: دریافت تاریخچه وضعیت‌های سفارش
  getOrderHistory: async (id) => {
    const response = await api.get(`/operations/orders/history/${id}/`);
    return response.data;
  },

  createOrder: async (data) => {
    const payload = {
      ...data,
      items: data.items.map(item => ({
        ...item,
        selections: item.selections || {} 
      }))
    };
    const response = await api.post("/order/", payload);
    return response.data;
  },

  deleteOrder: async (id) => {
    await api.delete(`/order/${id}/`);
  },

  updateStatus: async (id, statusCode, description) => {
    const response = await api.post(`/operations/transition/${id}/`, {
      new_status_code: statusCode,
      description,
    });
    return response.data;
  },

  approveOrder: async (id) => {
    const response = await api.post(`/operations/orders/${id}/approve/`);
    return response.data;
  },

  rejectOrder: async (id, description) => {
    const response = await api.post(`/operations/orders/${id}/reject/`, { description });
    return response.data;
  },

  changeStatus: async (id, statusCode, description = "") => {
    const response = await api.post(`/operations/transition/${id}/`, {
      new_status_code: statusCode,
      description
    });
    return response.data;
  },

  getStatusList: async () => {
    const response = await api.get("/operations/order/status/list/");
    return response.data;
  },

  uploadAttachment: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/operations/attachments/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data; 
  },
};