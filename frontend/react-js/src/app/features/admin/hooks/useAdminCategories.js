// src/app/features/admin/categories/hooks/useAdminCategories.js
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminCategoryService } from '../services/adminCategoryService';
import toast from 'react-hot-toast';
import Fuse from 'fuse.js';

export const useAdminCategories = () => {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  
  // صفحه بندی کلاینت ساید (چون API لیست کامل ریشه‌ها را می‌دهد)
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. Fetch Roots Only
  const { data: categories = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['admin-categories-roots'],
    queryFn: () => adminCategoryService.getRoots(),
    staleTime: 1000 * 60 * 2, // 2 دقیقه کش
  });

  // 2. Client-Side Processing
  const processedData = useMemo(() => {
    let result = [...categories];

    // جستجو
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'slug'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    // فیلتر وضعیت
    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      result = result.filter(cat => cat.is_active === isActive);
    }

    // سورت
    result.sort((a, b) => {
      const aVal = a[sortConfig.key] || '';
      const bVal = b[sortConfig.key] || '';
      if (aVal === bVal) return 0;
      const comparison = aVal > bVal ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [categories, searchQuery, statusFilter, sortConfig]);

  // Pagination
  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Mutations
  const toggleStatusMutation = useMutation({
    mutationFn: adminCategoryService.bulkStatus,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories-roots']);
      toast.success('وضعیت تغییر کرد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  const deleteMutation = useMutation({
    mutationFn: adminCategoryService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories-roots']);
      toast.success('دسته‌بندی حذف شد');
    },
    onError: () => toast.error('حذف ناموفق (احتمالا دارای زیرمجموعه است)'),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminCategoryService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories-roots']);
      toast.success('حذف گروهی انجام شد');
    },
  });

  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    categories: paginatedData,
    totalItems: processedData.length,
    totalPages,
    currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    statusFilter, setStatusFilter,
    sortConfig, handleSort,
    isLoading,
    toggleStatusMutation,
    deleteMutation,
    bulkDeleteMutation,
  };
};