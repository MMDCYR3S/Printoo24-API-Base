import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { adminOrderService } from '../services/adminOrderService';

export const useAdminOrders = () => {
  const queryClient = useQueryClient();
  
  // استیت‌های محلی
  const [currentPage, setCurrentPage] = useState(1);
  const [statusIdFilter, setStatusIdFilter] = useState('all'); // مقدار پیش‌فرض 'all'
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [dateFilter, setDateFilter] = useState('');

  // دبانس سرچ
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setCurrentPage(1);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // ریست صفحه با تغییر فیلترها
  useEffect(() => {
    setCurrentPage(1);
  }, [statusIdFilter, dateFilter]);

  // پارامترهای ارسالی به بک‌آند (فیلتر وضعیت را به بک‌آند نمی‌فرستیم تا کل دیتا بیاید)
  const queryParams = {
    page: currentPage,
    ...(debouncedSearch && { search: debouncedSearch }),
    ...(dateFilter && { date: dateFilter })
  };

  const { data = {}, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['admin-orders', queryParams],
    queryFn: () => adminOrderService.getAll(queryParams),
    staleTime: 0,
  });

  // ۱. استخراج آرایه خام سفارشات از ریسپانس بک‌آند
  const rawOrders = Array.isArray(data) ? data : (data.results || []);

  // ۲. اعمال فیلتر وضعیت روی فرانت‌اندر (مقایسه با current_status_code)
  const orders = rawOrders.filter(order => {
    if (statusIdFilter !== 'all' && statusIdFilter !== '') {
      return order.current_status_code === statusIdFilter;
    }
    return true;
  });

  // تنظیمات صفحه‌بندی بر اساس دیتای فیلتر شده واقعی
  const totalCount = statusIdFilter !== 'all' && statusIdFilter !== '' ? orders.length : (data.count || rawOrders.length);
  const itemsPerPage = 10;
  const totalPages = data.total_pages || Math.ceil(totalCount / itemsPerPage) || 1;

  // Mutations
  const deleteMutation = useMutation({
    mutationFn: adminOrderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      toast.success('سفارش حذف شد');
    },
    onError: () => toast.error('خطا در حذف سفارش'),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminOrderService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      toast.success('سفارشات انتخاب شده حذف شدند');
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  const changeStatusMutation = useMutation({
    mutationFn: ({ id, data }) => adminOrderService.changeStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      toast.success('وضعیت سفارش آپدیت شد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  return {
    orders, // این الان فقط سفارشات فیلتر شده واقعی رو پس میده
    totalCount,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusIdFilter,
    setStatusIdFilter,
    dateFilter,
    setDateFilter,
    isLoading,
    isFetching,
    refetch,
    deleteMutation,
    bulkDeleteMutation,
    changeStatusMutation
  };
};