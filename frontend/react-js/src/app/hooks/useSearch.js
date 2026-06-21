// src/app/hooks/useSearch.js
import { useState, useEffect, useCallback } from 'react';
import { shopService } from '../services/shopService';

export const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  // این اندپوینت pagination ندارد → hasMore همیشه false
  const [hasMore] = useState(false);

  // ریست کردن نتایج هنگام تغییر کلمه کلیدی
  useEffect(() => {
    setResults([]);
  }, [query]);

  const fetchResults = useCallback(async () => {
    if (!query || query.length < 2) return;

    setLoading(true);
    try {
      const data = await shopService.searchProducts(query);
      if (Array.isArray(data)) {
        setResults(data);
      }
    } catch (error) {
      console.error('Search Error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query]);

  // Debouncing: صبر کردن برای اتمام تایپ یوزر
  useEffect(() => {
    if (!query || query.length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      fetchResults();
    }, 500);

    return () => clearTimeout(timer);
  }, [query, fetchResults]);

  // چون API pagination ندارد، loadMore هیچ‌کاری نمی‌کند
  const loadMore = () => {};

  return { results, loading, hasMore, loadMore };
};
