import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import Fuse from 'fuse.js';
// اصلاح مهم: ایمپورت سرویس درست که شما دارید
import { adminProductService } from '../services/adminProductService'; 
// نکته: اگر فایل سرویس داخل پوشه products/services است، مسیر را چک کنید:
// import { adminProductService } from '../products/services/adminProductService';

console.log("⚠️ HOOK LOADED: useAdminProducts");

export const useAdminProducts = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'id', direction: 'desc' });
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // 1. دریافت دیتا
  const { data: rawProducts = [], isLoading, error, refetch } = useQuery({
    queryKey: ['admin-products'],
    // اصلاح مهم: استفاده از متد getAll که داخل فایل adminProductService.js شماست
    queryFn: adminProductService.getAll, 
    staleTime: 1000 * 60 * 5,
  });

  // لاگ برای اطمینان
  if (error) console.error("❌ Hook Error:", error);
  if (rawProducts?.length) console.log("📦 Loaded Products:", rawProducts.length);

  // 2. پردازش دیتا
  const processedData = useMemo(() => {
    // ایمنی: اگر دیتا نال بود، آرایه خالی بده
    if (!rawProducts || !Array.isArray(rawProducts)) return [];

    let result = [...rawProducts];

    // جستجو
    if (searchQuery.trim()) {
      const fuse = new Fuse(result, {
        keys: ['name', 'code', 'slug'], // فیلدهای قابل جستجو
        threshold: 0.3,
      });
      result = fuse.search(searchQuery).map((r) => r.item);
    }

    // سورت
    result.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      // هندل کردن قیمت
      if (sortConfig.key === 'price') {
        const pA = typeof a.price === 'string' ? parseFloat(a.price) : a.price;
        const pB = typeof b.price === 'string' ? parseFloat(b.price) : b.price;
        return sortConfig.direction === 'asc' ? pA - pB : pB - pA;
      }

      // هندل کردن متن
      const valA = aValue ? String(aValue).toLowerCase() : '';
      const valB = bValue ? String(bValue).toLowerCase() : '';

      if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
      if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [rawProducts, searchQuery, sortConfig]);

  // 3. صفحه‌بندی
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return processedData.slice(startIndex, startIndex + itemsPerPage);
  }, [processedData, currentPage]);

  const totalPages = Math.ceil(processedData.length / itemsPerPage) || 1;

  const handleSort = (key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  return {
    products: paginatedData,
    // لیست کامل برای دراپ‌داون ثبت سفارش
    allProducts: processedData || [], 
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