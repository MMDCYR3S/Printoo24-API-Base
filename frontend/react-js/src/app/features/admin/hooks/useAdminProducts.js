// src/app/features/admin/hooks/useAdminProducts.js
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Fuse from 'fuse.js';
import { adminService } from '../services/adminService';

export const useAdminProducts = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'id', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. دریافت دیتا از سرور
  const { data: rawProducts, isLoading, error, refetch } = useQuery({
    queryKey: ['admin-products'],
    queryFn: adminService.getAllProducts,
    staleTime: 1000 * 60 * 5, // 5 دقیقه کش
  });

  // 2. پردازش دیتا (جستجو و سورت)
  const processedData = useMemo(() => {
    if (!rawProducts) return [];

    let result = [...rawProducts];

    // الف) جستجو با Fuse.js
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'code', 'category'], // فیلدهای قابل جستجو
        threshold: 0.3, // میزان حساسیت (0 دقیق، 1 خیلی بیخیال)
      });
      result = fuse.search(searchQuery).map((r) => r.item);
    }

    // ب) سورت کردن
    result.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      // هندل کردن اعداد و رشته‌ها
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      // هندل کردن قیمت (چون استرینگ است)
      if (sortConfig.key === 'price') {
        return sortConfig.direction === 'asc' 
          ? parseFloat(a.price) - parseFloat(b.price) 
          : parseFloat(b.price) - parseFloat(a.price);
      }

      return sortConfig.direction === 'asc'
        ? String(aValue).localeCompare(String(bValue))
        : String(bValue).localeCompare(String(aValue));
    });

    return result;
  }, [rawProducts, searchQuery, sortConfig]);

  // 3. صفحه‌بندی (Pagination)
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return processedData.slice(startIndex, startIndex + itemsPerPage);
  }, [processedData, currentPage]);

  const totalPages = Math.ceil(processedData.length / itemsPerPage);

  // هندلرها
  const handleSort = (key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    products: paginatedData,
    totalItems: processedData.length,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    sortConfig,
    handleSort,
    isLoading,
    error,
    refetch,
  };
};