import api from "@/api/client";

// نگاشت کننده (Mapper) برای تبدیل فرمت فرم به فرمت بک‌ند
// این تابع باعث میشه کامپوننت‌های ما درگیر ساختار پیچیده JSON نشن
const mapOrderToApiPayload = (data) => {
  return {
    user_id: data.user_id,
    address_id: data.address_id,
    description: data.description,
    price: data.price, // قیمت کل
    items: data.items.map((item) => ({
      product_slug: item.product_name, // طبق توافق: نام محصول به عنوان اسلاگ میره
      quantity: item.quantity,
      // تمام ویژگی‌های فرعی میره توی selections
      selections: {
        custom_width: item.width || 0,
        custom_height: item.height || 0,
        description: item.description || "",
      },
    })),
  };
};

export const orderService = {
  // دریافت لیست کل سفارشات (مشترک برای همه)
  getAllOrders: async (params) => {
    const response = await api.get("/order/", { params });
    return response.data;
  },

  // دریافت جزئیات یک سفارش خاص
  getOrderById: async (id) => {
    const response = await api.get(`/order/${id}/`);
    return response.data;
  },

  // ایجاد سفارش (اختصاصی ادمین)
createOrder: async (data) => {
    // تبدیل دیتا در صورت نیاز (مثلا اگر selections خالی بود، آبجکت خالی بفرستیم)
    const payload = {
      ...data,
      items: data.items.map(item => ({
        ...item,
        // اطمینان از اینکه selections حتما آبجکت باشه حتی اگه پر نشده
        selections: item.selections || {} 
      }))
    };
    
    // ارسال به اندپوینت جدید
    const response = await api.post("/order/", payload);
    return response.data;
  },

  // حذف سفارش
  deleteOrder: async (id) => {
    await api.delete(`/order/${id}/`);
  },

  // آپدیت وضعیت (مشترک برای تغییر استاتوس)
  updateStatus: async (id, statusCode, description) => {
    const response = await api.post(`/operations/transition/${id}/`, {
      new_status_code: statusCode,
      description,
    });
    return response.data;
  },
  
  // تایید خودکار (Next Step)
  approveOrder: async (id) => {
    await api.post(`/operations/orders/${id}/approve/`);
  },
  
  // رد کردن سفارش (Reject)
  rejectOrder: async (id, description) => {
    await api.post(`/operations/orders/${id}/reject/`, { description });
  },

  getStatusList: async () => {
    const response = await api.get("/operations/order/status/list/");
    return response.data;
  },

  // متد آپلود فایل (تکی یا گروهی بسته به ساختار بکند)
  uploadAttachment: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/operations/attachments/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data; // فرض بر این است که ID یا URL برمی‌گرداند
  },


  approveOrder: async (id) => {
    const response = await api.post(`/operations/orders/${id}/approve/`);
    return response.data;
  },

  // رد کردن سفارش (Reject) با دلیل
  rejectOrder: async (id, description) => {
    const response = await api.post(`/operations/orders/${id}/reject/`, { description });
    return response.data;
  },

  // تغییر وضعیت به یک کد خاص (Transition)
  changeStatus: async (id, statusCode, description = "") => {
    const response = await api.post(`/operations/transition/${id}/`, {
      new_status_code: statusCode,
      description
    });
    return response.data;
  }

};

