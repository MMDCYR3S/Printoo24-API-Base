import { useState, useEffect } from 'react'; // useEffect اضافه شد
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'; // useQuery اضافه شد
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { adminOrderService } from '../services/adminOrderService';
import { customerService } from '../services/customerService'; // این سرویس را ایمپورت کنید


const orderSchema = z.object({
  user_id: z.number().min(1, 'انتخاب کاربر الزامی است'),
  // اگر آدرس اجباری نیست یا کاربر آدرس نداره، باید هندل بشه. فعلاً عدد می‌گیریم
  address_id: z.number().optional().nullable(),
});

export const useOrderCreate = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [step, setStep] = useState(1);
  const totalSteps = 3;
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedAddressId, setSelectedAddressId] = useState(null); // استیت جدید برای آدرس
  const [cartItems, setCartItems] = useState([]);

  // --- دریافت جزئیات کاربر (شامل آدرس‌ها) ---
  const { data: userDetails, isLoading: isLoadingUser } = useQuery({
    queryKey: ['admin-customer-details', selectedUser?.id],
    queryFn: () => customerService.getById(selectedUser.id),
    enabled: !!selectedUser?.id, // فقط وقتی کاربر انتخاب شده اجرا شود
  });

  // وقتی کاربر عوض شد، آدرس قبلی را پاک کن
  useEffect(() => {
    setSelectedAddressId(null);
  }, [selectedUser]);

  // محاسبه قیمت
  const calculateTotal = () => {
    return cartItems.reduce((acc, item) => {
      const price = parseFloat(item.product?.price || 0);
      return acc + (item.quantity * price);
    }, 0);
  };

  const createMutation = useMutation({
    mutationFn: (data) => adminOrderService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-orders']);
      toast.success('سفارش با موفقیت ثبت شد');
      navigate('/admin/orders');
    },
    onError: (err) => {
      console.error("Order Submit Error:", err.response?.data);
      const msg = err.response?.data?.detail || err.response?.data?.message || 'خطا در ثبت سفارش';
      toast.error(msg);
    }
  });

  const submitOrder = () => {
    if (!selectedUser) return toast.error('کاربر انتخاب نشده است');
    // بررسی انتخاب آدرس (اگر سرور اجباری کرده)
    if (!selectedAddressId) return toast.error('لطفاً یک آدرس برای سفارش انتخاب کنید');
    if (cartItems.length === 0) return toast.error('سبد خرید خالی است');

    const totalPrice = calculateTotal();

    const payload = {
      user_id: parseInt(selectedUser.id),
      // ارسال آدرس واقعی انتخاب شده
      address_id: parseInt(selectedAddressId), 
      price: String(totalPrice),
      items: cartItems.map(item => ({
        product_slug: item.product.slug,
        selections: {
          quantity: parseInt(item.quantity),
          size_id: item.size?.id ? parseInt(item.size.id) : 0, // اگر سایز اجباری نیست 0 یا null
          custom_width: item.width ? parseInt(item.width) : 0,
          custom_height: item.height ? parseInt(item.height) : 0,
          option_value_ids: [],
          has_design: false
        }
      }))
    };

    console.log("Sending Payload:", payload);
    createMutation.mutate(payload);
  };

  // ... (nextStep و prevStep بدون تغییر) ...
  const nextStep = () => {
    if (step === 1) {
       if (!selectedUser) return toast.error('لطفاً کاربر را انتخاب کنید');
       // اینجا می‌تونیم اجبار کنیم که آدرس هم تو مرحله ۱ انتخاب بشه
       if (!selectedAddressId) return toast.error('لطفاً آدرس ارسال را انتخاب کنید');
    }
    if (step === 2 && cartItems.length === 0) return toast.error('حداقل یک محصول اضافه کنید');
    setStep(prev => Math.min(prev + 1, totalSteps));
  };

  const prevStep = () => setStep(prev => Math.max(prev - 1, 1));

  return {
    step,
    totalSteps,
    nextStep,
    prevStep,
    selectedUser,
    setSelectedUser,
    userDetails, // جزئیات کامل کاربر (شامل آدرس‌ها) رو پاس میدیم
    selectedAddressId,
    setSelectedAddressId,
    cartItems,
    setCartItems,
    submitOrder,
    isSubmitting: createMutation.isPending,
    calculateTotal
  };
};