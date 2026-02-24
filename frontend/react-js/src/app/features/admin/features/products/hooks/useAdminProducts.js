import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../services/adminProductService';
import { adminCategoryService } from '../../../services/adminCategoryService';

// تابع نرمال‌سازی برای مقایسه دقیق متون فارسی
const normalize = (text) => {
  if (!text) return '';
  return text.toString().trim()
    .replace(/ي/g, 'ی').replace(/ك/g, 'ک')
    .replace(/\s+/g, '') 
    .toLowerCase();
};

export const useAdminProducts = () => {
  const queryClient = useQueryClient();
  
  // --- States ---
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilterId, setCategoryFilterId] = useState('all'); 
  const [statusFilter, setStatusFilter] = useState('all');
  // سورتینگ فقط بر اساس زمان
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // --- Queries ---
  const { data: products = [], isLoading: pLoading, refetch } = useQuery({
    queryKey: ['admin-products'],
    queryFn: adminProductService.getAll,
    staleTime: 1000 * 60 * 2,
  });

  // دریافت دسته‌بندی‌ها (فقط ریشه‌ها که داخلشون children دارن)
  const { data: categories = [], isLoading: cLoading } = useQuery({
    queryKey: ['admin-categories-dropdown'],
    queryFn: adminCategoryService.getRoots,
  });

  // --- Processing Logic ---
  const processedProducts = useMemo(() => {
    if (!products || !Array.isArray(products)) return [];

    let result = [...products];

    // 1. فیلتر دسته‌بندی هوشمند (پدر + تمام فرزندان)
    if (categoryFilterId !== 'all') {
      const selectedRoot = categories.find(c => String(c.id) === String(categoryFilterId));
      if (selectedRoot) {
        // جمع‌آوری نام دسته اصلی و تمام زیردسته‌های آن
        const validCategoryNames = [selectedRoot.name];
        if (selectedRoot.children && selectedRoot.children.length > 0) {
           selectedRoot.children.forEach(child => validCategoryNames.push(child.name));
        }
        
        const normalizedValidNames = validCategoryNames.map(normalize);
        
        result = result.filter(p => {
          if (!p.category) return false;
          return normalizedValidNames.includes(normalize(p.category));
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

    // 4. مرتب‌سازی (فقط زمان)
    result.sort((a, b) => {
      let aVal = new Date(a.created_at || 0).getTime();
      let bVal = new Date(b.created_at || 0).getTime();

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
    
    categoryFilterId, setCategoryFilterId,
    statusFilter, setStatusFilter,
    categories,

    sortConfig, handleSort,
    isLoading: pLoading || cLoading,
    refetch,
    
    bulkDeleteMutation,
    bulkStatusMutation
  };
};