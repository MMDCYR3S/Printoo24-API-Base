import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminArticleService } from '../../../services/adminArticleService';
import toast from 'react-hot-toast';
import Fuse from 'fuse.js';

export const useAdminArticles = () => {
  const queryClient = useQueryClient();
  const QUERY_KEY = ['admin-articles'];

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: 'published_at', direction: 'desc' });
  
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const { data: articles = [], isLoading, isError, refetch } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: adminArticleService.getAll,
    staleTime: 1000 * 60 * 2,
  });

  const { data: minimalProducts = [] } = useQuery({
    queryKey: ['minimal-products'],
    queryFn: adminArticleService.getMinimalProducts,
  });

  // پردازش سمت کلاینت (جستجو، فیلتر، مرتب‌سازی)
  const processedData = useMemo(() => {
    let result = [...articles];

    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['title', 'summary', 'slug', 'category_name'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    if (statusFilter !== 'all') {
      result = result.filter(article => article.status === statusFilter);
    }

    result.sort((a, b) => {
      // برای هندل کردن مقادیر null یا undefined
      const aVal = a[sortConfig.key] || '';
      const bVal = b[sortConfig.key] || '';
      
      if (aVal === bVal) return 0;
      const comparison = aVal > bVal ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [articles, searchQuery, statusFilter, sortConfig]);

  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSort = (key) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  // Mutations
  const deleteMutation = useMutation({
    mutationFn: adminArticleService.delete,
    onSuccess: () => {
      toast.success('مقاله با موفقیت حذف شد');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در حذف مقاله'),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminArticleService.bulkDelete,
    onSuccess: () => {
      toast.success('مقالات انتخاب‌شده حذف شدند');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  const bulkStatusMutation = useMutation({
    mutationFn: adminArticleService.bulkStatus,
    onSuccess: () => {
      toast.success('وضعیت مقالات بروزرسانی شد');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  const publishMutation = useMutation({
    mutationFn: adminArticleService.quickPublish,
    onSuccess: () => {
      toast.success('مقاله با موفقیت منتشر شد');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در انتشار مقاله'),
  });

  return {
    articles: paginatedData,
    totalItems: processedData.length,
    totalPages,
    currentPage, setCurrentPage,
    searchQuery, setSearchQuery,
    statusFilter, setStatusFilter,
    sortConfig, handleSort,
    minimalProducts,
    isLoading,
    isError,
    refetch,
    deleteMutation,
    bulkDeleteMutation,
    bulkStatusMutation,
    publishMutation
  };
};