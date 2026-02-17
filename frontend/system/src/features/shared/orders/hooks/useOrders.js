import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { orderService } from "../api/orderService";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

// ... (بقیه کدهای قبلی مثل ORDER_KEYS و useCreateOrder و useOrders سر جایشان باشند)

export const ORDER_KEYS = {
  all: ["orders"],
  detail: (id) => ["orders", id],
};

export const useCreateOrder = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: orderService.createOrder,
    onSuccess: () => {
      toast.success("سفارش با موفقیت ثبت شد");
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all });
      navigate("/admin/orders");
    },
    onError: (error) => {
      const message = error.response?.data?.message || "خطا در ثبت سفارش";
      toast.error(message);
    },
  });
};

export const useOrders = (params) => {
  return useQuery({
    queryKey: [...ORDER_KEYS.all, params],
    queryFn: () => orderService.getAllOrders(params),
    keepPreviousData: true,
  });
};

export const useOrderStatusList = () => {
  return useQuery({
    queryKey: ["order-statuses"],
    queryFn: orderService.getStatusList,
    staleTime: 1000 * 60 * 30,
  });
};

// 👇 اصلاح اصلی اینجاست: اضافه شدن changeStatus
export const useOrderActions = () => {
  const queryClient = useQueryClient();

  // 1. Approve
  const approve = useMutation({
    mutationFn: orderService.approveOrder,
    onSuccess: () => {
      toast.success("سفارش به مرحله بعد منتقل شد");
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: () => toast.error("خطا در تایید سفارش")
  });
  
  // 2. Reject
  const reject = useMutation({
    mutationFn: ({ id, description }) => orderService.rejectOrder(id, description),
    onSuccess: () => {
      toast.success("سفارش رد شد");
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: () => toast.error("خطا در رد سفارش")
  });

  // 3. Change Status (اینی که جا افتاده بود!)
  const changeStatus = useMutation({
    mutationFn: ({ id, statusCode, description }) => 
        orderService.changeStatus(id, statusCode, description),
    onSuccess: () => {
      toast.success("وضعیت سفارش تغییر کرد");
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: (err) => {
        // نمایش خطای دقیق سرور اگر موجود باشد
        const msg = err.response?.data?.detail || "خطا در تغییر وضعیت";
        toast.error(msg);
    }
  });

  return { 
      approve, 
      reject, 
      changeStatus, // ✅ حالا این اکسپورت می‌شود و ارور رفع می‌شود
      isChanging: changeStatus.isPending 
  };
};