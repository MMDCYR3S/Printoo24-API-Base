import { useState, useEffect, useCallback } from 'react';
import { blogService } from '../../../services/blogService';

export const useArticleDetail = (slugOrId) => {
  const [article, setArticle] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchArticle = useCallback(async () => {
    if (!slugOrId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const data = await blogService.getArticleById(slugOrId);
      setArticle(data);
    } catch (err) {
      setError('کێشەیەک لە وەرگرتنی زانیارییەکانی بلاگەکە ڕوویدا.');
      console.error('Error fetching article details:', err);
    } finally {
      setIsLoading(false);
    }
  }, [slugOrId]);

  useEffect(() => {
    fetchArticle();
  }, [fetchArticle]);

  return { article, isLoading, error };
};