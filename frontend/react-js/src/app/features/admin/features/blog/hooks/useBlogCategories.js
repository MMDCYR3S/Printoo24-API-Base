import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminBlogCategoryService } from '../../../services/adminBlogCategoryService';
import toast from 'react-hot-toast'; // یا هر کتابخانه نوتیفیکیشن دیگر

const QUERY_KEY = 'blog-categories';

export const useBlogCategories = () => {
  return useQuery({
    queryKey: [QUERY_KEY],
    queryFn: adminBlogCategoryService.getAll,
  });
};

export const useCreateBlogCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminBlogCategoryService.create,
    onSuccess: () => {
      toast.success('دسته‌بندی با موفقیت ایجاد شد');
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
    onError: () => toast.error('خطا در ایجاد دسته‌بندی'),
  });
};

export const useUpdateBlogCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminBlogCategoryService.update,
    onSuccess: () => {
      toast.success('دسته‌بندی با موفقیت ویرایش شد');
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
    onError: () => toast.error('خطا در ویرایش دسته‌بندی'),
  });
};

export const useDeleteBlogCategory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminBlogCategoryService.delete,
    onSuccess: () => {
      toast.success('دسته‌بندی حذف شد');
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
    onError: () => toast.error('خطا در حذف دسته‌بندی'),
  });
};

export const useBulkDeleteBlogCategories = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminBlogCategoryService.bulkDelete,
    onSuccess: () => {
      toast.success('موارد انتخاب شده حذف شدند');
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
    onError: () => toast.error('خطا در حذف گروهی'),
  });
};

export const useBulkStatusBlogCategories = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: adminBlogCategoryService.bulkStatus,
    onSuccess: () => {
      toast.success('وضعیت موارد انتخاب شده تغییر کرد');
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] });
    },
    onError: () => toast.error('خطا در تغییر وضعیت گروهی'),
  });
};