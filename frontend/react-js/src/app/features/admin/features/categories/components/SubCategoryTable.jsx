// src/app/features/admin/categories/components/SubCategoryTable.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Edit, Trash2, Eye, CheckCircle2, XCircle, Image as ImageIcon, CornerDownRight } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminCategoryService } from '../../../services/adminCategoryService';
import toast from 'react-hot-toast';
import clsx from 'clsx';

const SubCategoryTable = () => {
  const queryClient = useQueryClient();

  // دریافت فقط زیردسته‌ها
  const { data: subCategories = [], isLoading } = useQuery({
    queryKey: ['admin-subcategories'],
    queryFn: adminCategoryService.getAllSubCategories,
  });

  // عملیات حذف (تکراری اما لازم برای استقلال کامپوننت)
  const deleteMutation = useMutation({
    mutationFn: adminCategoryService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-subcategories']);
      toast.success('زیردسته حذف شد');
    },
    onError: () => toast.error('خطا در حذف'),
  });

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این زیردسته اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div className="text-center py-10"><span className="loading loading-spinner text-primary"></span></div>;

  return (
    <div className="overflow-x-auto bg-white rounded-2xl border border-slate-100 shadow-sm">
      <table className="table w-full">
        <thead className="bg-slate-50 text-xs uppercase font-bold text-slate-500">
          <tr>
            <th className="w-16">تصویر</th>
            <th>نام زیردسته</th>
            <th>دسته مادر (والد)</th>
            <th className="text-center">وضعیت</th>
            <th className="text-left pl-6">عملیات</th>
          </tr>
        </thead>
        <tbody>
          {subCategories.length === 0 ? (
             <tr><td colSpan="5" className="text-center py-8 text-slate-400">هیچ زیردسته‌ای یافت نشد.</td></tr>
          ) : (
            subCategories.map((cat) => (
              <tr key={cat.id} className="hover:bg-slate-50 border-b border-slate-50 last:border-0">
                <td>
                  <div className="avatar">
                    <div className="w-10 h-10 rounded-lg ring-1 ring-slate-100 bg-slate-50 p-0.5">
                      {cat.banner_box ? (
                        <img src={cat.banner_box} alt={cat.name} className="object-cover rounded-md" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-300"><ImageIcon size={16}/></div>
                      )}
                    </div>
                  </div>
                </td>
                
                <td>
                  <div className="font-bold text-slate-700 text-sm">{cat.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono mt-1 dir-ltr text-right">/{cat.slug}</div>
                </td>

                {/* نمایش نام والد */}
                <td>
                    {cat.parent_name ? (
                        <span className="badge badge-ghost gap-1 text-xs bg-blue-50 text-blue-700 border-0">
                            <CornerDownRight size={12}/>
                            {cat.parent_name}
                        </span>
                    ) : (
                        <span className="text-xs text-error">-- بدون والد --</span>
                    )}
                </td>

                <td className="text-center">
                    {cat.is_active ? 
                        <span className="text-emerald-500 text-xs font-bold bg-emerald-50 px-2 py-1 rounded">فعال</span> : 
                        <span className="text-slate-400 text-xs bg-slate-100 px-2 py-1 rounded">غیرفعال</span>
                    }
                </td>

                <td>
                  <div className="flex justify-end gap-1">
                    {/* لینک به جزئیات */}
                    <Link to={`/admin/categories/detail/${cat.id}`} className="btn btn-xs btn-ghost btn-square text-slate-400 hover:text-primary">
                        <Eye size={16} />
                    </Link>
                    {/* لینک به ویرایش */}
                    <Link to={`/admin/categories/edit/${cat.id}`} className="btn btn-xs btn-ghost btn-square text-slate-400 hover:text-blue-600">
                        <Edit size={16} />
                    </Link>
                    <button onClick={() => handleDelete(cat.id)} className="btn btn-xs btn-ghost btn-square text-slate-400 hover:text-red-500">
                        <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

export default SubCategoryTable;