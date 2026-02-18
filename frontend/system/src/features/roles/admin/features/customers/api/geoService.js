import api from "@/api/client";

export const geoService = {
  // دریافت لیست استان‌ها
  getProvinces: async () => {
    const response = await api.get("/users/geo/provinces/");
    return response.data;
  },

  // دریافت لیست شهرها بر اساس آیدی استان
  getCities: async (provinceId) => {
    if (!provinceId) return [];
    const response = await api.get(`/users/geo/cities/`, {
      params: { province_id: provinceId }
    });
    return response.data;
  }
};