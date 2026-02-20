import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { adminOrderService } from '../services/adminOrderService';

export const useAdminOrders = () => {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // --- States (Syncing with URL params for better UX) ---
  const initialPage = parseInt(searchParams.get('page')) || 1;
  const initialStatus = searchParams.get('status_id') || 'all';
  const initialSearch = searchParams.get('search') || '';
  const initialDate = searchParams.get('date') || ''; // فرمت YYYY-MM-DD

  const [currentPage, setCurrentPage] = useState(initialPage);
  const [statusIdFilter, setStatusIdFilter] = useState(initialStatus);
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [debouncedSearch, setDebouncedSearch] = useState(initialSearch);
  const [dateFilter, setDateFilter] = useState(initialDate);

  // Debounce Search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      if (searchQuery !== initialSearch) setCurrentPage(1);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery, initialSearch]);

  // Update URL Params when filters change
  useEffect(() => {
    const params = {};
    if (currentPage > 1) params.page = currentPage;
    if (statusIdFilter !== 'all') params.status_id = statusIdFilter;
    if (debouncedSearch) params.search = debouncedSearch;
    if (dateFilter) params.date = dateFilter;
    setSearchParams(params, { replace: true });
  }, [currentPage, statusIdFilter, debouncedSearch, dateFilter, setSearchParams]);

  // --- Fetch Data ---
  const queryParams = {
    page: currentPage,
    ...(debouncedSearch && { search: debouncedSearch }),
    ...(statusIdFilter !== 'all' && { status_id: statusIdFilter }),
    ...(dateFilter && { date: dateFilter })
  };

  const { data = {}, isLoading, isFetching, refetch } = useQuery({
    queryKey: ['admin-orders', queryParams],
    queryFn: () => adminOrderService.getAll(queryParams),
    staleTime: 1000 * 30, // 30 ثانیه کش
  });

  const orders = Array.isArray(data) ? data : (data.results || []);
  const totalCount = data.count || orders.length;
  const itemsPerPage = 10;
  const totalPages = data.total_pages || Math.ceil(totalCount / itemsPerPage) || 1;

// --- Mutations ---
  const deleteMutation = useMutation({
    mutationFn: adminOrderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      refetch();
      toast.success('سفارش حذف شد');
    },
    onError: () => toast.error('خطا در حذف سفارش'),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminOrderService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      refetch();
      toast.success('سفارشات انتخاب شده حذف شدند');
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  const changeStatusMutation = useMutation({
    mutationFn: ({ id, data }) => adminOrderService.changeStatus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      refetch(); // این باعث میشه جدول درجا بدون نیاز به F5 زدن آپدیت بشه
      toast.success('وضعیت با موفقیت تغییر کرد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  return {
    orders,
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
    isFetching, // برای نشان دادن لودینگ‌های ریز (مثلاً هنگام تایپ)
    refetch,
    deleteMutation,
    bulkDeleteMutation,
    changeStatusMutation
  };
};