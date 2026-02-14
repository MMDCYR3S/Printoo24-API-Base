import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "../api/customerService";
import { toast } from "sonner";

const CUSTOMER_KEYS = {
  all: ["customers"],
  addresses: (userId) => ["customers", userId, "addresses"],
};

// هوک جستجوی مشتری (برای Select Box)
export const useCustomerSearch = (searchTerm) => {
  return useQuery({
    queryKey: [...CUSTOMER_KEYS.all, { search: searchTerm }],
    queryFn: () => customerService.searchCustomers(searchTerm),
    // فقط زمانی اجرا شود که سرچ ترم وجود داشته باشد (برای جلوگیری از ریکوئست اضافه)
    // یا اگر استراتژی این است که اول لیست خالی باشد
    enabled: true, 
    staleTime: 1000 * 60 * 5, // 5 دقیقه کش بماند
  });
};

// هوک دریافت آدرس‌های یک مشتری
export const useCustomerAddresses = (userId) => {
  return useQuery({
    queryKey: CUSTOMER_KEYS.addresses(userId),
    queryFn: () => customerService.getCustomerAddresses(userId),
    enabled: !!userId, // تا وقتی یوزر انتخاب نشده، ریکوئست نزن
  });
};

// هوک ثبت سریع مشتری
export const useCreateQuickCustomer = (onSuccessCallback) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: customerService.createQuickCustomer,
    onSuccess: (newCustomer) => {
      toast.success(`مشتری ${newCustomer.first_name} ${newCustomer.last_name} ساخته شد`);
      // لیست مشتریان را رفرش کن
      queryClient.invalidateQueries({ queryKey: CUSTOMER_KEYS.all });
      
      // اگر کال‌بکی پاس داده شده (مثلا بستن مودال) اجرا کن
      if (onSuccessCallback) onSuccessCallback(newCustomer);
    },
    onError: (error) => {
      const msg = error.response?.data?.username ? "نام کاربری تکراری است" : "خطا در ثبت مشتری";
      toast.error(msg);
    },
  });
};