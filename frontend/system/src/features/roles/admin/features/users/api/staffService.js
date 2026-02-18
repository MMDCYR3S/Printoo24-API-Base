import api from "@/api/client";

export const staffService = {
  // دریافت لیست پرسنل
  getAllStaff: async () => {
    const response = await api.get("/users/staff/");
    return response.data;
  },

  // استخدام کارمند جدید
  createStaff: async (data) => {
    const response = await api.post("/users/staff/", data);
    return response.data;
  },

  // ویرایش کارمند (فقط نقش و وضعیت طبق داکیومنت)
  updateStaff: async ({ id, data }) => {
    const response = await api.put(`/users/staff/${id}/`, data);
    return response.data;
  },

  // اخراج (حذف)
  deleteStaff: async (id) => {
    await api.delete(`/users/staff/${id}/`);
  },

  // عملیات گروهی
  bulkAction: async ({ action, ids, data = {} }) => {
    // action: 'delete' | 'activate' | 'deactivate' | 'change_role'
    // data: برای change_role مثلا { role_id: 5 } لازم است
    const body = { ids, ...data };
    const response = await api.post(`/users/staff/actions/${action}/`, body);
    return response.data;
  },

  // دریافت لیست نقش‌ها (فرضی - چون اندپوینت نقش‌ها رو ندادی)
  // اگر اندپوینت جداگانه داری جایگزین کن، وگرنه فعلا این کار میکنه
  getAllRoles: async () => {
    // فرض میکنیم این اندپوینت وجود داره. اگه نداری، فعلا هاردکد کن یا اندپوینت درست رو بذار
    try {
        const response = await api.get("/users/roles/"); 
        return response.data;
    } catch (e) {
        // دیتای تستی برای اینکه صفحه خراب نشه تا وقتی API نقش رو بدی
        return [
            { id: 1, name: "مدیر کل", label: "Super Admin" },
            { id: 2, name: "حسابدار", label: "Accountant" },
            { id: 3, name: "انباردار", label: "Warehouse" },
            { id: 4, name: "اپراتور چاپ", label: "Print Operator" },
            { id: 5, name: "طراح", label: "Designer" },
        ];
    }
  }
};