import api from "@/api/client";

export const customerService = {
  // جستجوی مشتری (برای کمبوباکس انتخاب مشتری)
  searchCustomers: async (query) => {
    // فرض بر اینه که اندپوینت لیست مشتریان قابلیت سرچ داره یا همه رو میده
    // اگر کوئری پارامتر search داره: params: { search: query }
    const response = await api.get("/users/customers/");
    
    // فیلترینگ کلاینت‌ساید (اگر بک‌ند سرچ نداره) - موقت
    if (query) {
      return response.data.filter(c => 
        c.first_name.includes(query) || 
        c.last_name.includes(query) || 
        c.phone_number.includes(query)
      );
    }
    return response.data;
  },

  // دریافت آدرس‌های یک مشتری خاص (برای دراپ‌داون آدرس)
  getCustomerAddresses: async (userId) => {
    const response = await api.get(`/users/customers/${userId}/addresses/`);
    return response.data; // آرایه‌ای از آدرس‌ها برمی‌گرداند
  },

  // ثبت سریع مشتری جدید (Modal)
  createQuickCustomer: async (customerData) => {
    const response = await api.post("/users/customers/", customerData);
    return response.data;
  }
};