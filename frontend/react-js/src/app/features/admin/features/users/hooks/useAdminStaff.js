import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminStaffService } from '../../../services/adminStaffService';
import { toast } from 'react-hot-toast';

export const useAdminStaff = () => {
  const queryClient = useQueryClient();

  const staffQuery = useQuery({
    queryKey: ['admin-staffs'],
    queryFn: adminStaffService.getAll,
  });

  const rolesQuery = useQuery({
    queryKey: ['admin-staff-roles'],
    queryFn: adminStaffService.getRoles,
  });

  const createMutation = useMutation({
    mutationFn: adminStaffService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('کارمند جدید ایجاد شد');
    },
    onError: () => toast.error('خطا در ایجاد کارمند')
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => adminStaffService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('اطلاعات کارمند بروزرسانی شد');
    },
    onError: () => toast.error('خطا در ویرایش کارمند')
  });

  const deleteMutation = useMutation({
    mutationFn: adminStaffService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('کارمند حذف شد');
    }
  });

  const bulkRoleMutation = useMutation({
    mutationFn: adminStaffService.bulkChangeRole,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('نقش کارمندان تغییر کرد');
    }
  });

  const bulkStatusMutation = useMutation({
    mutationFn: adminStaffService.bulkToggleStatus,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('وضعیت تغییر کرد');
    }
  });

  const bulkDeleteMutation = useMutation({
    mutationFn: adminStaffService.bulkDelete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-staffs']);
      toast.success('کارمندان انتخاب شده حذف شدند');
    }
  });

  return {
    staffQuery,
    rolesQuery,
    createMutation,
    updateMutation,
    deleteMutation,
    bulkRoleMutation,
    bulkStatusMutation,
    bulkDeleteMutation
  };
};