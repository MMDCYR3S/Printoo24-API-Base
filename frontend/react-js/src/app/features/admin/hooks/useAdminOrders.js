import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js'; // برای جستجوی هوشمند
import toast from 'react-hot-toast';
import { adminOrderService } from '../services/adminOrderService';

export const useAdminOrders = () => {
  const queryClient = useQueryClient();
  
  // --- States ---
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, paid, pending, cancelled, ...
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // --- 1. Fetch Data ---
  const { data: rawOrders = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-orders'],
    queryFn: adminOrderService.getAll,
    staleTime: 1000 * 60 * 2, // 2 دقیقه کش
  });

  // --- Mutations ---
  
  // حذف تکی
  const deleteMutation = useMutation({
    mutationFn: adminOrderService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-orders']);
      toast.success('سفارش با موفقیت حذف شد');
    },
    onError: () => toast.error('خطا در حذف سفارش (شاید فاکتور شده باشد)'),
  });

  // حذف گروهی
  const bulkDeleteMutation = useMutation({
    mutationFn: adminOrderService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-orders']);
      toast.success('سفارشات انتخاب شده حذف شدند');
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  // --- 2. Processing Data (Search -> Filter -> Sort) ---
  const processedOrders = useMemo(() => {
    let result = [...rawOrders];

    // الف) فیلتر وضعیت (Status)
    if (statusFilter !== 'all') {
      // فرض بر این است که status_name یا یک فیلد مشابه برای وضعیت داریم
      // اینجا باید با دیتای واقعی چک کنی که دقیقاً چه استرینگی برمی‌گردد
      result = result.filter(order => order.status_name === statusFilter);
    }

    // ب) جستجو (Fuzzy Search)
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['id', 'username', 'user_info', 'total_price'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    // ج) سورت (Sorting)
    result.sort((a, b) => {
      let aValue = a[sortConfig.key];
      let bValue = b[sortConfig.key];

      // هندل کردن قیمت و اعداد
      if (sortConfig.key === 'total_price' || sortConfig.key === 'id') {
        aValue = parseFloat(aValue) || 0;
        bValue = parseFloat(bValue) || 0;
      }

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [rawOrders, searchQuery, statusFilter, sortConfig]);

  // --- 3. Pagination ---
  const totalPages = Math.ceil(processedOrders.length / itemsPerPage);
  const paginatedOrders = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return processedOrders.slice(start, start + itemsPerPage);
  }, [processedOrders, currentPage]);

  // --- Handlers ---
  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    orders: paginatedOrders,
    totalCount: processedOrders.length,
    rawCount: rawOrders.length,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    sortConfig,
    handleSort,
    isLoading,
    isError,
    refetch,
    deleteMutation,
    bulkDeleteMutation
  };
};