import { useQuery } from "@tanstack/react-query";
import { geoService } from "../api/geoService";

export const useProvinces = () => {
  return useQuery({
    queryKey: ["provinces"],
    queryFn: geoService.getProvinces,
    staleTime: Infinity, // استان‌ها به ندرت تغییر می‌کنند
  });
};

export const useCities = (provinceId) => {
  return useQuery({
    queryKey: ["cities", provinceId],
    queryFn: () => geoService.getCities(provinceId),
    enabled: !!provinceId, // تا استان انتخاب نشود، درخواست نزن
  });
};