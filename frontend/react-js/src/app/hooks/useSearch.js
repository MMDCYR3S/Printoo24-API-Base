// src/app/hooks/useSearch.js
import { useState, useEffect } from 'react';
import { shopService } from '../services/shopService';

export const useSearch = (query) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const hasMore = false;

  useEffect(() => {
    // اگه query خالی یا کمتر از ۲ کاراکتر بود، پاک کن و برگرد
    if (!query || query.trim().length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }

    let isCancelled = false; // جلوگیری از race condition

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await shopService.searchProducts(query.trim());
        if (!isCancelled) {
          setResults(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error('Search Error:', error);
        if (!isCancelled) {
          setResults([]);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }, 500);

    return () => {
      isCancelled = true; // کنسل کردن ریکوئست قبلی
      clearTimeout(timer);
    };
  }, [query]); // فقط query به عنوان dependency

  const loadMore = () => {};

  return { results, loading, hasMore, loadMore };
};