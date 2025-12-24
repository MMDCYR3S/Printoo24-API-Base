// src/app/features/admin/products/hooks/useAdminProducts.js
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';
import { adminCategoryService } from '../../../services/adminCategoryService'; // مسیر سرویس کتگوری را چک کن

// تابع نرمال‌سازی برای مقایسه دقیق متون فارسی
const normalize = (text) => {
  if (!text) return '';
  return text.toString().trim()
    .replace(/ي/g, 'ی').replace(/ك/g, 'ک')
    .replace(/\s+/g, '') // حذف تمام فاصله‌ها برای مقایسه سخت‌گیرانه
    .toLowerCase();
};

export const useAdminProducts = () => {
  const queryClient = useQueryClient();
  
  // --- States ---
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilterId, setCategoryFilterId] = useState('all'); // ID دسته‌بندی
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // --- Queries ---
  // 1. دریافت محصولات
  const { data: products = [], isLoading: pLoading, refetch } = useQuery({
    queryKey: ['admin-products'],
    queryFn: adminProductService.getAll,
    staleTime: 1000 * 60 * 2,
  });

  // 2. دریافت دسته‌بندی‌ها (حیاتی برای فیلتر)
  const { data: categories = [], isLoading: cLoading } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminCategoryService.getAll,
  });

  // --- Processing Logic ---
  const processedProducts = useMemo(() => {
    if (!products || !Array.isArray(products)) return [];

    let result = [...products];

    // 1. فیلتر دسته‌بندی (Mapping ID -> Name)
    if (categoryFilterId !== 'all') {
      // پیدا کردن نام دسته‌بندی از روی ID انتخاب شده
      const selectedCat = categories.find(c => String(c.id) === String(categoryFilterId));
      
      if (selectedCat) {
        const targetName = normalize(selectedCat.name);
        result = result.filter(p => {
          if (!p.category) return false;
          // مقایسه نام نرمال شده محصول با نام نرمال شده دسته‌بندی
          return normalize(p.category).includes(targetName);
        });
      }
    }

    // 2. فیلتر وضعیت
    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      result = result.filter(p => p.is_active === isActive);
    }

    // 3. جستجو (Fuzzy Search)
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'code', 'slug', 'category'],
        threshold: 0.35,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    // 4. مرتب‌سازی
    result.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];

      if (sortConfig.key === 'price') {
        aVal = parseFloat(aVal) || 0;
        bVal = parseFloat(bVal) || 0;
      }
      
      if (sortConfig.key === 'created_at') {
        aVal = new Date(aVal || 0).getTime();
        bVal = new Date(bVal || 0).getTime();
      }

      aVal = aVal ?? '';
      bVal = bVal ?? '';

      if (aVal === bVal) return 0;
      const comparison = aVal > bVal ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [products, categories, searchQuery, categoryFilterId, statusFilter, sortConfig]);

  // --- Pagination ---
  const totalPages = Math.ceil(processedProducts.length / itemsPerPage) || 1;
  const paginatedProducts = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return processedProducts.slice(start, start + itemsPerPage);
  }, [processedProducts, currentPage, itemsPerPage]);

  // --- Mutations ---
  const bulkDeleteMutation = useMutation({
    mutationFn: adminProductService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-products']);
      toast.success('محصولات انتخاب شده حذف شدند');
    },
    onError: () => toast.error('خطا در حذف محصولات')
  });

  const bulkStatusMutation = useMutation({
    mutationFn: adminProductService.bulkStatus,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-products']);
      toast.success('وضعیت تغییر کرد');
    },
    onError: () => toast.error('خطا در تغییر وضعیت')
  });

  // --- Stats Calculation ---
  const stats = useMemo(() => ({
    total: products.length,
    active: products.filter(p => p.is_active).length,
    inactive: products.filter(p => !p.is_active).length,
  }), [products]);

  const handleSort = (key) => {
    setSortConfig(curr => ({
      key,
      direction: curr.key === key && curr.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  return {
    products: paginatedProducts,
    allProducts: products,
    stats,
    totalItems: processedProducts.length,
    totalPages,
    currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    
    categoryFilterId, setCategoryFilterId, // دقت کن: اینجا ID ست میشه
    statusFilter, setStatusFilter,
    categories,

    sortConfig, handleSort,
    isLoading: pLoading || cLoading,
    refetch,
    
    bulkDeleteMutation,
    bulkStatusMutation
  };
};