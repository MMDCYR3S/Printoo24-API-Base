import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerService } from '../../../services/customerService';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export const useCustomers = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // 1. دریافت لیست همه کاربران
  const usersQuery = useQuery({
    queryKey: ['admin-customers'],
    queryFn: () => customerService.getAll(),
    staleTime: 1000 * 60 * 5, // 5 دقیقه
  });

  // 2. دریافت اطلاعات یک کاربر خاص (این بخش قبلاً نبود و باعث ارور شد)
  const useCustomer = (id) => useQuery({
    queryKey: ['admin-customer', id],
    queryFn: () => customerService.getById(id),
    enabled: !!id, // فقط وقتی id وجود دارد اجرا شود
  });

  // ایجاد کاربر
  const createMutation = useMutation({
    mutationFn: customerService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success('کاربر جدید با موفقیت ایجاد شد');
    },
    onError: (err) => {
      toast.error(err?.response?.data?.message || 'خطا در ایجاد کاربر');
    }
  });

  // ویرایش کاربر
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => customerService.update(id, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries(['admin-customers']);
      // آپدیت کش صفحه دیتیل همان کاربر
      queryClient.invalidateQueries(['admin-customer', variables.id]);
      toast.success('اطلاعات کاربر به‌روز شد');
    },
    onError: (err) => {
      toast.error(err?.response?.data?.message || 'خطا در ویرایش کاربر');
    }
  });

  // حذف تکی
  const deleteMutation = useMutation({
    mutationFn: customerService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success('کاربر حذف شد');
      navigate('/dashboard/users'); // بازگشت به لیست بعد از حذف
    },
    onError: () => toast.error('خطا در حذف کاربر')
  });

  // عملیات گروهی: تغییر وضعیت
  const bulkStatusMutation = useMutation({
    mutationFn: customerService.bulkStatus,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success('وضعیت کاربران تغییر کرد');
    }
  });

  // عملیات گروهی: حذف
  const bulkDeleteMutation = useMutation({
    mutationFn: customerService.bulkDelete,
    onSuccess: (ids) => {
      queryClient.invalidateQueries(['admin-customers']);
      toast.success(`${ids.length} کاربر حذف شدند`);
    }
  });

  return {
    usersQuery,
    useCustomer, // <--- این تابع باید حتما اینجا باشد
    createMutation,
    updateMutation,
    deleteMutation,
    bulkStatusMutation,
    bulkDeleteMutation
  };
};