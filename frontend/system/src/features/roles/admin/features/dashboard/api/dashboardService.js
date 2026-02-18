import api from "@/api/client";

export const dashboardService = {
  getAdminDashboard: async () => {
    const response = await api.get("/operations/dashboard/admin/");
    return response.data;
  }
};