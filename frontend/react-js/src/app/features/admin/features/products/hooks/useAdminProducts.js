// src/app/features/admin/products/hooks/useAdminProducts.js
import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';
// فرض بر این است که سرویس کتگوری دارید، اگر نه، این بخش را کامنت کنید
import { adminCategoryService } from '../../../services/adminCategoryService'; 

export const useAdminProducts = () => {
  const queryClient = useQueryClient();
  
  // States
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all'); // ID دسته یا 'all'
  const [statusFilter, setStatusFilter] = useState('all'); // 'active', 'inactive', 'all'
  const [sortConfig, setSortConfig] = useState({ key: 'id', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. دریافت دیتا
  const { data: products = [], isLoading, refetch } = useQuery({
    queryKey: ['admin-products'],
    queryFn: adminProductService.getAll,
    staleTime: 1000 * 60 * 2, // 2 دقیقه دیتا تازه میماند
  });

  // دریافت دسته‌بندی‌ها برای فیلتر (اختیاری)
  const { data: categories = [] } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminCategoryService?.getAll || (() => []), // Fallback
    enabled: !!adminCategoryService,
  });

  // 2. پردازش دیتا (Search -> Filter -> Sort)
  const processedProducts = useMemo(() => {
    let result = [...products];

    // A. جستجو (Fuse.js)
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'code', 'slug'], 
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    // B. فیلتر دسته‌بندی
    if (categoryFilter !== 'all') {
      result = result.filter(p => p.category === Number(categoryFilter));
    }

    // C. فیلتر وضعیت
    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      result = result.filter(p => p.is_active === isActive);
    }

    // D. مرتب‌سازی (Sort)
    result.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];

      // هندل کردن قیمت (رشته به عدد)
      if (sortConfig.key === 'price') {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [products, searchQuery, categoryFilter, statusFilter, sortConfig]);

  // 3. صفحه‌بندی
  const totalPages = Math.ceil(processedProducts.length / itemsPerPage);
  const paginatedProducts = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return processedProducts.slice(start, start + itemsPerPage);
  }, [processedProducts, currentPage]);

  // --- Mutations (Bulk Actions) ---

  // حذف گروهی
  const bulkDeleteMutation = useMutation({
    mutationFn: adminProductService.bulkDelete,
    onMutate: async (ids) => {
      // Optimistic Update
      await queryClient.cancelQueries(['admin-products']);
      const previousData = queryClient.getQueryData(['admin-products']);
      
      queryClient.setQueryData(['admin-products'], (old) => 
        old?.filter(p => !ids.includes(p.id))
      );
      
      toast.success(`${ids.length} محصول حذف شدند`);
      return { previousData };
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['admin-products'], context.previousData);
      toast.error('خطا در حذف محصولات');
    },
    onSettled: () => queryClient.invalidateQueries(['admin-products']),
  });

  // تغییر وضعیت گروهی
  const bulkStatusMutation = useMutation({
    mutationFn: adminProductService.bulkStatus,
    onMutate: async ({ product_ids, is_active }) => {
      await queryClient.cancelQueries(['admin-products']);
      const previousData = queryClient.getQueryData(['admin-products']);

      queryClient.setQueryData(['admin-products'], (old) => 
        old?.map(p => product_ids.includes(p.id) ? { ...p, is_active } : p)
      );

      toast.success(`وضعیت ${product_ids.length} محصول تغییر کرد`);
      return { previousData };
    },
    onError: (err, vars, context) => {
      queryClient.setQueryData(['admin-products'], context.previousData);
      toast.error('خطا در تغییر وضعیت');
    },
    onSettled: () => queryClient.invalidateQueries(['admin-products']),
  });

  const handleSort = (key) => {
    setSortConfig(curr => ({
      key,
      direction: curr.key === key && curr.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  return {
    products: paginatedProducts,
    totalItems: processedProducts.length,
    totalPages,
    currentPage,
    setCurrentPage,
    // Filters
    searchQuery, setSearchQuery,
    categoryFilter, setCategoryFilter,
    statusFilter, setStatusFilter,
    categories, // برای پر کردن سلکت باکس
    // Sort
    sortConfig, handleSort,
    // Loading
    isLoading, refetch,
    // Mutations
    bulkDeleteMutation,
    bulkStatusMutation,
  };
};