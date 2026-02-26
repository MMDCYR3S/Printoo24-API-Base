import { useState, useEffect, useCallback } from 'react';
import { blogService } from '../../../services/blogService';

export const useTutorials = () => {
  const [tutorials, setTutorials] = useState([]);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [listError, setListError] = useState(null);

  // استیت‌های مربوط به مودال جزئیات
  const [selectedTutorial, setSelectedTutorial] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // دریافت لیست آموزش‌ها
  const fetchTutorials = useCallback(async () => {
    setIsLoadingList(true);
    setListError(null);
    try {
      const data = await blogService.getTutorials();
      // پشتیبانی از پجینیشن احتمالی بک‌اند
      setTutorials(data.results || data || []);
    } catch (err) {
      setListError('مشکلی در دریافت لیست آموزش‌ها به وجود آمد.');
      console.error('Error fetching tutorials:', err);
    } finally {
      setIsLoadingList(false);
    }
  }, []);

  useEffect(() => {
    fetchTutorials();
  }, [fetchTutorials]);

  // باز کردن مودال و دریافت جزئیات دقیق آموزش
  const handleOpenTutorial = async (id) => {
    setIsModalOpen(true);
    setIsLoadingDetail(true);
    setDetailError(null);
    try {
      const data = await blogService.getTutorialById(id);
      setSelectedTutorial(data);
    } catch (err) {
      setDetailError('مشکلی در دریافت جزئیات ویدیو به وجود آمد.');
      console.error('Error fetching tutorial detail:', err);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  // بستن مودال و پاک‌سازی دیتا با کمی تاخیر برای انیمیشن
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => {
      setSelectedTutorial(null);
    }, 300); 
  };

  return {
    tutorials,
    isLoadingList,
    listError,
    selectedTutorial,
    isLoadingDetail,
    detailError,
    isModalOpen,
    handleOpenTutorial,
    handleCloseModal
  };
};