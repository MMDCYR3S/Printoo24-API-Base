import api from "@/api/client"; // همان ایمپورت خودتان

export const customerService = {
  // ============================================================
  // بخش ۱: متدهای قدیمی (مخصوص ثبت سفارش) - بدون تغییر 🔒
  // ============================================================

  // جستجوی مشتری (برای کمبوباکس انتخاب مشتری)
  searchCustomers: async (query = "") => {
    // نکته: این متد هم برای سرچ باکس سفارش کار میکنه هم برای لیست مشتریان CRM
    const response = await api.get("/users/customers/");
    
    // فیلترینگ کلاینت‌ساید (حفظ لاجیک قبلی شما)
    if (query && typeof query === 'string') {
      const lowerQuery = query.toLowerCase();
      return response.data.filter(c => 
        (c.first_name && c.first_name.toLowerCase().includes(lowerQuery)) || 
        (c.last_name && c.last_name.toLowerCase().includes(lowerQuery)) || 
        (c.phone_number && c.phone_number.includes(lowerQuery)) ||
        (c.company && c.company.toLowerCase().includes(lowerQuery)) // شرکت را هم اضافه کردم برای سرچ بهتر
      );
    }
    return response.data;
  },

  // دریافت آدرس‌های یک مشتری خاص
  getCustomerAddresses: async (userId) => {
    const response = await api.get(`/users/customers/${userId}/addresses/`);
    return response.data;
  },

  // ثبت سریع مشتری (برای مودال سفارش)
  createQuickCustomer: async (customerData) => {
    const response = await api.post("/users/customers/", customerData);
    return response.data;
  },

  // ============================================================
  // بخش ۲: متدهای جدید (مخصوص پنل مدیریت مشتریان) - اضافه شده 🆕
  // ============================================================

  // دریافت یک مشتری خاص با جزئیات کامل (برای فرم ویرایش)
  getCustomerById: async (id) => {
    const response = await api.get(`/users/customers/${id}/`);
    return response.data;
  },

  // ویرایش مشتری
  updateCustomer: async ({ id, data }) => {
    const response = await api.put(`/users/customers/${id}/`, data);
    return response.data;
  },

  // حذف مشتری
  deleteCustomer: async (id) => {
    await api.delete(`/users/customers/${id}/`);
  },

  // عملیات گروهی (حذف و ...)
  bulkAction: async ({ action, ids }) => {
    const response = await api.post(`/users/customers/bulk/${action}/`, { ids });
    return response.data;
  },

// متد جدید: ایجاد آدرس برای مشتری
  createAddress: async ({ userId, addressData }) => {
    const response = await api.post(`/users/customers/${userId}/addresses/`, addressData);
    return response.data;
  },
  
  // اینم که قبلا داشتیم ولی اینجا برای اطمینان میذارم
  createCustomer: async (data) => {
    const response = await api.post("/users/customers/", data);
    return response.data;
  },

  // ... (کدهای قبلی سرجاشون باشه)

  // -------------------------------------------
  // بخش مدیریت آدرس‌ها (تکمیل شده)
  // -------------------------------------------
  
  // ایجاد آدرس (قبلاً بود)
  createAddress: async ({ userId, addressData }) => {
    const response = await api.post(`/users/customers/${userId}/addresses/`, addressData);
    return response.data;
  },

  // ویرایش آدرس (جدید)
  updateAddress: async ({ userId, addressId, addressData }) => {
    const response = await api.put(`/users/customers/${userId}/addresses/${addressId}/`, addressData);
    return response.data;
  },

  // حذف آدرس (جدید)
  deleteAddress: async ({ userId, addressId }) => {
    await api.delete(`/users/customers/${userId}/addresses/${addressId}/`);
  }


};

