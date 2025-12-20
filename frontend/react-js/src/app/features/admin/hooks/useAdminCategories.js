// src/app/features/admin/categories/hooks/useAdminCategories.js
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminCategoryService } from '../services/adminCategoryService';
import toast from 'react-hot-toast';
import Fuse from 'fuse.js'; // برای جستجوی فازی کلاینت ساید

export const useAdminCategories = () => {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all, active, inactive
  const [parentFilter, setParentFilter] = useState('all'); // all, root, sub
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. Fetch Data
  const { data: categories = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: () => adminCategoryService.getAll(),
    staleTime: 1000 * 60 * 5, // 5 دقیقه دیتا تازه می‌ماند
  });

  // 2. Client-Side Processing (Search, Filter, Sort)
  const processedData = useMemo(() => {
    let result = [...categories];

    // الف) جستجو (Fuzzy Search)
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'slug', 'description'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    // ب) فیلتر وضعیت
    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      result = result.filter(cat => cat.is_active === isActive);
    }

    // پ) فیلتر والد/فرزند
    if (parentFilter !== 'all') {
      if (parentFilter === 'root') result = result.filter(cat => !cat.parent);
      if (parentFilter === 'sub') result = result.filter(cat => cat.parent);
    }

    // ت) سورت
    result.sort((a, b) => {
      const aVal = a[sortConfig.key] || '';
      const bVal = b[sortConfig.key] || '';
      
      if (aVal === bVal) return 0;
      
      const comparison = aVal > bVal ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [categories, searchQuery, statusFilter, parentFilter, sortConfig]);

  // 3. Pagination
  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // 4. Mutations (با Optimistic Updates)
  
  // تغییر وضعیت (تکی یا گروهی)
  const toggleStatusMutation = useMutation({
    mutationFn: adminCategoryService.bulkStatus,
    onMutate: async ({ ids, active }) => {
      await queryClient.cancelQueries(['admin-categories']);
      const previousData = queryClient.getQueryData(['admin-categories']);

      // آپدیت فوری UI
      queryClient.setQueryData(['admin-categories'], (old) => 
        old.map(cat => ids.includes(cat.id) ? { ...cat, is_active: active } : cat)
      );

      return { previousData };
    },
    onError: (err, newCtx, context) => {
      queryClient.setQueryData(['admin-categories'], context.previousData);
      toast.error('خطا در تغییر وضعیت');
    },
    onSettled: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success('وضعیت به‌روزرسانی شد');
    },
  });

  // حذف (تکی)
  const deleteMutation = useMutation({
    mutationFn: adminCategoryService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success('دسته‌بندی حذف شد');
    },
    onError: () => toast.error('این دسته قابل حذف نیست (شاید زیرمجموعه دارد)'),
  });

  // حذف گروهی
  const bulkDeleteMutation = useMutation({
    mutationFn: adminCategoryService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success('موارد انتخاب شده حذف شدند');
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  // هندلر سورت
  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    categories: paginatedData,
    allCategoriesRaw: categories, // برای استفاده در مودال (انتخاب والد)
    totalItems: processedData.length,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    parentFilter,
    setParentFilter,
    sortConfig,
    handleSort,
    isLoading,
    toggleStatusMutation,
    deleteMutation,
    bulkDeleteMutation,
  };
};