import apiClient from '../../../services/apiClient'; // مسیر فایل اینستنس اکسیوس خود را جایگزین کنید

export const adminBlogCategoryService = {
  // دریافت لیست همه دسته‌ها
  getAll: async () => {
    const response = await apiClient.get('/dashboard/blog-categories/');
    return response.data;
  },

  // دریافت جزئیات یک دسته
  getById: async (id) => {
      const response = await apiClient.get(`/dashboard/blog-categories/${id}/`);
      return response.data;
    },

  // ایجاد دسته جدید
  create: async (data) => {
    const response = await apiClient.post('/dashboard/blog-categories/', data);
    return response.data;
  },

  // ویرایش دسته
  update: async ({ id, data }) => {
    const response = await apiClient.put(`/dashboard/blog-categories/${id}/`, data);
    return response.data;
  },

  // حذف تکی
  delete: async (id) => {
    const response = await apiClient.delete(`/dashboard/blog-categories/${id}/`);
    return response.data;
  },

  // حذف گروهی (فرض بر این است که بک‌اند آرایه ids را در body دریافت می‌کند)
  bulkDelete: async (ids) => {
    const response = await apiClient.delete('/dashboard/blog-categories/bulk-delete/', {
      data: { ids }
    });
    return response.data;
  },

  // تغییر وضعیت گروهی
  bulkStatus: async ({ ids, status }) => {
    const response = await apiClient.patch('/dashboard/blog-categories/bulk-status/', {
      ids,
      status
    });
    return response.data;
  }
};