import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminTutorialService } from '../../../services/adminTutorialService';
import toast from 'react-hot-toast';
import Fuse from 'fuse.js';

export const useAdminTutorials = () => {
  const queryClient = useQueryClient();
  const QUERY_KEY = ['admin-tutorials'];

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // دریافت لیست آموزش‌ها
  const { data: tutorials = [], isLoading, isError, refetch } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: adminTutorialService.getAll,
  });

  // دریافت محصولات برای دراپ‌داون
  const { data: minimalProducts = [] } = useQuery({
    queryKey: ['minimal-products'],
    queryFn: adminTutorialService.getMinimalProducts,
  });

  // پردازش سمت کلاینت (جستجو، فیلتر، مرتب‌سازی)
  const processedData = useMemo(() => {
    let result = [...tutorials];

    if (searchQuery.trim()) {
      const fuse = new Fuse(result, { keys: ['title', 'slug'], threshold: 0.3 });
      result = fuse.search(searchQuery).map(r => r.item);
    }

    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      result = result.filter(tutorial => tutorial.is_active === isActive);
    }

    result.sort((a, b) => {
      const aVal = a[sortConfig.key] || '';
      const bVal = b[sortConfig.key] || '';
      if (aVal === bVal) return 0;
      const comparison = aVal > bVal ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [tutorials, searchQuery, statusFilter, sortConfig]);

  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handleSort = (key) => {
    setSortConfig(current => ({
      key, direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  // Mutations
  const deleteMutation = useMutation({
    mutationFn: adminTutorialService.delete,
    onSuccess: () => {
      toast.success('آموزش با موفقیت حذف شد');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در حذف آموزش'),
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminTutorialService.bulkDelete,
    onSuccess: () => {
      toast.success('موارد انتخاب‌شده حذف شدند');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });

  const bulkStatusMutation = useMutation({
    mutationFn: adminTutorialService.bulkStatus,
    onSuccess: () => {
      toast.success('وضعیت آموزش‌ها بروزرسانی شد');
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
    onError: () => toast.error('خطا در تغییر وضعیت'),
  });

  return {
    tutorials: paginatedData, totalItems: processedData.length, totalPages,
    currentPage, setCurrentPage,
    searchQuery, setSearchQuery, statusFilter, setStatusFilter, sortConfig, handleSort,
    minimalProducts, isLoading, isError, refetch,
    deleteMutation, bulkDeleteMutation, bulkStatusMutation
  };
};