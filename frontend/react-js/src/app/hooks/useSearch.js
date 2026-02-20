// src/app/hooks/useSearch.js
import { useState, useEffect, useCallback } from 'react';
import { shopService } from '../services/shopService';

export const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // ریست کردن نتایج هنگام تغییر کلمه کلیدی
  useEffect(() => {
    setResults([]);
    setPage(1);
    setHasMore(true);
  }, [query]);

  const fetchResults = useCallback(async (pageNum) => {
    if (!query || query.length < 2) return;
    
    setLoading(true);
    try {
      const data = await shopService.searchProducts(query, pageNum);
      
      if (Array.isArray(data)) {
        setResults(prev => pageNum === 1 ? data : [...prev, ...data]);
        // اگر تعداد نتایج کمتر از حد انتظار بود، یعنی صفحه بعدی وجود ندارد
        if (data.length < 10) setHasMore(false); 
      }
    } catch (error) {
      console.error("Search Error:", error);
    } finally {
      setLoading(false);
    }
  }, [query]);

  // Debouncing: صبر کردن برای اتمام تایپ یوزر
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query) fetchResults(1);
    }, 500); // 500ms delay

    return () => clearTimeout(timer);
  }, [query, fetchResults]);

  const loadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchResults(nextPage);
    }
  };

  return { results, loading, hasMore, loadMore };
};