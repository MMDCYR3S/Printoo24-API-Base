import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminProvinceService, adminCityService } from '../services/adminLocationService';
import toast from 'react-hot-toast';

// --- هوک مدیریت استان‌ها ---
export const useProvinces = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  
  // Fetch
  const { data: provinces = [], isLoading } = useQuery({
    queryKey: ['admin-provinces'],
    queryFn: adminProvinceService.getAll,
  });

  // Filter & Sort (Client-side)
  const filteredData = useMemo(() => {
    if (!provinces) return [];
    return provinces.filter(p => p.name.includes(searchTerm));
  }, [provinces, searchTerm]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: adminProvinceService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-provinces']);
      toast.success('استان جدید اضافه شد');
    },
  });

  const updateMutation = useMutation({
    mutationFn: adminProvinceService.update,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-provinces']);
      toast.success('استان ویرایش شد');
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminProvinceService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-provinces']);
      toast.success('استان‌های انتخاب شده حذف شدند');
    },
  });

  return {
    provinces: filteredData,
    allProvinces: provinces, // برای استفاده در سلکت باکس شهرها
    isLoading,
    searchTerm,
    setSearchTerm,
    createMutation,
    updateMutation,
    bulkDeleteMutation,
  };
};

// --- هوک مدیریت شهرها ---
export const useCities = () => {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvinceId, setSelectedProvinceId] = useState('all');

  // Fetch (وابسته به فیلتر استان)
  const { data: cities = [], isLoading } = useQuery({
    queryKey: ['admin-cities', selectedProvinceId],
    queryFn: () => adminCityService.getAll(selectedProvinceId),
  });

  // Client-side Search
  const filteredData = useMemo(() => {
    if (!cities) return [];
    return cities.filter(c => c.name.includes(searchTerm));
  }, [cities, searchTerm]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: adminCityService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-cities']);
      toast.success('شهر جدید اضافه شد');
    },
  });

  const updateMutation = useMutation({
    mutationFn: adminCityService.update,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-cities']);
      toast.success('شهر ویرایش شد');
    },
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminCityService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-cities']);
      toast.success('شهرهای انتخاب شده حذف شدند');
    },
  });

  return {
    cities: filteredData,
    isLoading,
    searchTerm,
    setSearchTerm,
    selectedProvinceId,
    setSelectedProvinceId,
    createMutation,
    updateMutation,
    bulkDeleteMutation
  };
};