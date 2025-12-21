// src/app/features/admin/hooks/useAdminMessages.js
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import toast from 'react-hot-toast';
import { adminContactService } from '../services/adminContactService';

export const useAdminMessages = () => {
  const queryClient = useQueryClient();
  
  // States
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState('all'); // all, unread, read, replied, pending
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });

  // 1. Fetch Data
  const { data: rawMessages = [], isLoading } = useQuery({
    queryKey: ['admin-messages'],
    queryFn: adminContactService.getAll,
    staleTime: 1000 * 60 * 2,
  });

  // 2. Mutations
  const replyMutation = useMutation({
    mutationFn: adminContactService.reply,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-messages']);
      toast.success('پاسخ شما با موفقیت ارسال شد');
    },
    onError: () => toast.error('خطا در ارسال پاسخ'),
  });

  const deleteMutation = useMutation({
    mutationFn: adminContactService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-messages']);
      toast.success('پیام با موفقیت حذف شد');
    },
    onError: () => toast.error('خطا در حذف پیام'),
  });

  // 3. Advanced Filtering & Searching
  const processedData = useMemo(() => {
    if (!rawMessages.length) return [];

    let result = [...rawMessages];

    // الف) فیلتر وضعیت
    if (statusFilter !== 'all') {
        result = result.filter(msg => {
            if (statusFilter === 'unread') return !msg.is_read;
            if (statusFilter === 'read') return msg.is_read;
            if (statusFilter === 'replied') return msg.admin_reply !== null; // یا msg.status_display.includes...
            if (statusFilter === 'pending') return msg.admin_reply === null;
            return true;
        });
    }

    // ب) جستجو
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['full_name', 'email', 'subject', 'phone_number', 'message'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map((r) => r.item);
    }

    // پ) مرتب‌سازی
    result.sort((a, b) => {
      const aValue = a[sortConfig.key] || '';
      const bValue = b[sortConfig.key] || '';

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [rawMessages, searchQuery, statusFilter, sortConfig]);

  // 4. Pagination
  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSort = (key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    messages: paginatedData,
    totalCount: processedData.length,
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
    replyMutation,
    deleteMutation
  };
};