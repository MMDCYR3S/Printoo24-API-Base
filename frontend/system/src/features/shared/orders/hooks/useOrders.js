import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { orderService } from "../api/orderService";
import { toast } from "sonner"; // برای نوتیفیکیشن
import { useNavigate } from "react-router-dom";

// کلیدهای کش برای مدیریت بهتر وضعیت
export const ORDER_KEYS = {
  all: ["orders"],
  detail: (id) => ["orders", id],
};

// هوک ایجاد سفارش (مخصوص ادمین)
export const useCreateOrder = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: orderService.createOrder,
    onSuccess: () => {
      toast.success("سفارش با موفقیت ثبت شد");
      // لیست سفارشات را نامعتبر می‌کنیم تا دوباره فچ شود
      queryClient.invalidateQueries({ queryKey: ORDER_KEYS.all });
      // هدایت به لیست سفارشات (یا صفحه جزئیات)
      navigate("/admin/orders");
    },
    onError: (error) => {
      // نمایش خطای سمت سرور یا خطای عمومی
      const message = error.response?.data?.message || "خطا در ثبت سفارش";
      toast.error(message);
    },
  });
};

// هوک دریافت لیست سفارشات (برای جدول)
export const useOrders = (params) => {
  return useQuery({
    queryKey: [...ORDER_KEYS.all, params],
    queryFn: () => orderService.getAllOrders(params),
    keepPreviousData: true, // برای صفحه بندی بهتر
  });
};

export const useOrderStatusList = () => {
  return useQuery({
    queryKey: ["order-statuses"],
    queryFn: orderService.getStatusList,
    staleTime: 1000 * 60 * 30, // ۳۰ دقیقه کش
  });
};

export const useOrderActions = () => {
  const queryClient = useQueryClient();

  // میوتاسیون برای Approve
  const approve = useMutation({
    mutationFn: orderService.approveOrder,
    onSuccess: () => {
      toast.success("سفارش به مرحله بعد منتقل شد");
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
    onError: () => toast.error("خطا در تغییر وضعیت")
  });
  

  // میوتاسیون برای Reject
  const reject = useMutation({
    mutationFn: ({ id, description }) => orderService.rejectOrder(id, description),
    onSuccess: () => {
      toast.success("سفارش رد شد");
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    }
  });

  return { approve, reject };
};