import { useQuery } from "@tanstack/react-query";
import apiClient from "../../../../api/client";
import { API_ENDPOINTS } from "../../../../config/constants";

const fetchOrders = async () => {
  const response = await apiClient.get(API_ENDPOINTS.ORDERS.LIST);
  // طبق داکیومنت Swagger، خروجی یک آرایه از آبجکت‌هاست
  return response.data; 
};

export const useOrders = () => {
  return useQuery({
    queryKey: ["orders"],
    queryFn: fetchOrders,
    staleTime: 1000 * 60 * 2, // 2 دقیقه کش
    retry: 1,
  });
};