import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { blogService } from '../../../services/blogService';

export const useBlog = () => {
  // استفاده از URL برای مدیریت فیلترها (به شدت برای سئو و لینک‌دهی مفیده)
  const [searchParams, setSearchParams] = useSearchParams();

  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // استخراج مقادیر فعلی از URL یا اعمال مقادیر پیش‌فرض
  const categoryId = searchParams.get('category') || null;
  const searchQuery = searchParams.get('search') || '';
  const ordering = searchParams.get('ordering') || '-published_at'; // دیفالت: جدیدترین
  const page = parseInt(searchParams.get('page') || '1', 10);

  // فچ کردن دسته‌بندی‌ها (فقط یک‌بار)
  const fetchCategories = useCallback(async () => {
    try {
      const data = await blogService.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  }, []);

  // فچ کردن مقالات بر اساس تغییرات فیلترها
  const fetchArticles = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {
        ...(categoryId && { category: categoryId }),
        ...(searchQuery && { search: searchQuery }),
        ...(ordering && { ordering }),
        page,
      };
      
      const data = await blogService.getArticles(params);
      
      // اگر بک‌اند دیتای پجینیت شده (شامل count, next, results) بفرسته
      // اینجا هندل می‌کنیم. فعلاً طبق داکیومنت قبلی فرض بر آرایه است.
      // اگر بک‌اند شما ساختار صفحه بندی داره، setArticles(data.results) میشه.
      setArticles(data.results || data || []); 
      
    } catch (err) {
      setError('Failed to load articles. Please try again later.');
      console.error('Error fetching articles:', err);
    } finally {
      setIsLoading(false);
    }
  }, [categoryId, searchQuery, ordering, page]);

  // اجرای لود دیتا
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  // تابع متمرکز برای آپدیت فیلترها در URL
  const handleFilterChange = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key); // اگر خالی بود (مثلا پاک کردن سرچ)، کلید رو از URL حذف کن
    }

    // اگر فیلتری غیر از شماره صفحه تغییر کرد، کاربر رو برگردون صفحه اول
    if (key !== 'page') {
      newParams.set('page', '1');
    }

    setSearchParams(newParams);
  };

  return {
    articles,
    categories,
    isLoading,
    error,
    filters: { categoryId, searchQuery, ordering, page },
    handleFilterChange,
  };
};