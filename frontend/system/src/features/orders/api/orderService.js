import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "../../../api/client";
import { API_ENDPOINTS } from "../../../config/constants";

// 1. تابع درخواست به سرور (Pure Function)
const fetchOrders = async () => {
  const response = await apiClient.get(API_ENDPOINTS.ORDERS.LIST);
  return response.data; // طبق داکیومنت، آرایه‌ای از سفارشات برمی‌گردد [cite: 98-120]
};

// 2. هوک اختصاصی برای استفاده در کامپوننت‌ها
export const useOrders = () => {
  return useQuery({
    queryKey: ["orders"], // کلید یکتا برای کش کردن دیتا
    queryFn: fetchOrders,
    staleTime: 1000 * 60 * 5, // دیتا تا 5 دقیقه تازه می‌ماند (جلوگیری از درخواست اضافی)
    retry: 1, // اگر ارور داد، فقط 1 بار تلاش مجدد کن
  });
};

// 3. هوک تغییر وضعیت سفارش (برای دکمه‌های تایید که در آینده می‌سازیم)
export const useApproveOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId) => {
      // طبق داکیومنت [cite: 172]
      return apiClient.post(API_ENDPOINTS.ORDERS.APPROVE(orderId));
    },
    onSuccess: () => {
      // بعد از تایید موفق، لیست سفارشات را رفرش کن تا وضعیت جدید را ببینیم
      queryClient.invalidateQueries(["orders"]);
    },
  });
};