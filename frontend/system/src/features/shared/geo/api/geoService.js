import api from "@/api/client";

export const geoService = {
  getProvinces: async () => {
    const response = await api.get("/users/geo/provinces/");
    return response.data;
  },

  getCities: async (provinceId) => {
    if (!provinceId) return [];
    const response = await api.get(`/users/geo/cities/?province_id=${provinceId}`);
    return response.data;
  },
};