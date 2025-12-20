// src/app/features/admin/hooks/useAdminMessages.js
import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import toast from 'react-hot-toast';
import { adminContactService } from '../services/adminContactService';

export const useAdminMessages = () => {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });

  // 1. Fetch Data
  const { data: rawMessages = [], isLoading } = useQuery({
    queryKey: ['admin-messages'],
    queryFn: adminContactService.getAll,
    staleTime: 1000 * 60 * 2, // 2 دقیقه کش
  });

  // 2. Mutation for Reply
  const replyMutation = useMutation({
    mutationFn: adminContactService.reply,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-messages']);
      toast.success('پاسخ شما با موفقیت ارسال شد');
    },
    onError: () => toast.error('خطا در ارسال پاسخ'),
  });

  // 3. Processing (Search & Sort)
  const processedData = useMemo(() => {
    if (!rawMessages.length) return [];

    let result = [...rawMessages];

    // Search
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['full_name', 'email', 'subject', 'phone_number'],
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map((r) => r.item);
    }

    // Sort
    result.sort((a, b) => {
      const aValue = a[sortConfig.key] || '';
      const bValue = b[sortConfig.key] || '';

      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [rawMessages, searchQuery, sortConfig]);

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
    sortConfig,
    handleSort,
    isLoading,
    replyMutation,
  };
};