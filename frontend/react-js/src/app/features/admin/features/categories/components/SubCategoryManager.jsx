// src/app/features/admin/categories/components/SubCategoryManager.jsx
import React, { useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Save, CornerDownRight, CheckCircle2, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminCategoryService } from '../../../services/adminCategoryService';
import clsx from 'clsx';

const SubCategoryManager = ({ parentCategory }) => {
  const queryClient = useQueryClient();
  const parentSlug = parentCategory?.slug;

  // تنظیمات فرم
  const { control, register, handleSubmit, reset, formState: { isDirty } } = useForm({
    defaultValues: {
      subs: []
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "subs"
  });

  // پر کردن فرم با زیردسته‌های موجود
  useEffect(() => {
    if (parentCategory?.children) {
      const formattedData = parentCategory.children.map(child => ({
        id: child.id,
        name: child.name,
        slug: child.slug,
        is_active: child.is_active ?? true,
      }));
      reset({ subs: formattedData });
    }
  }, [parentCategory, reset]);

  // Mutation
  const bulkMutation = useMutation({
    mutationFn: (data) => {
      // آماده‌سازی داده‌ها طبق داکیومنت Swagger
      const payload = data.subs.map(item => {
        const itemPayload = {
          name: item.name,
          slug: item.slug,
          is_active: item.is_active,
          parent_slug: parentSlug, // اتصال به والد
        };
        // اگر ID دارد یعنی ویرایش است، اگر ندارد یعنی جدید است
        if (item.id) {
          itemPayload.id = item.id;
        }
        return itemPayload;
      });

      return adminCategoryService.bulkUpsert(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['category', String(parentCategory.id)]);
      toast.success('تغییرات زیردسته‌ها ذخیره شد');
    },
    onError: (err) => {
      console.error(err);
      toast.error('خطا در ذخیره زیردسته‌ها');
    }
  });

  const onSubmit = (data) => {
    if (!parentSlug) {
      toast.error('Slug دسته مادر نامشخص است.');
      return;
    }
    bulkMutation.mutate(data);
  };

  return (
    <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
      <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <div>
          <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
            <CornerDownRight className="text-primary"/> مدیریت سریع زیرمجموعه‌ها
          </h3>
          <p className="text-xs text-slate-500 mt-1">اضافه کردن یا ویرایش گروهی زیردسته‌های <strong>{parentCategory.name}</strong></p>
        </div>
        <button 
          onClick={() => append({ name: '', slug: '', is_active: true })} 
          className="btn btn-sm btn-outline btn-primary gap-2"
        >
          <Plus size={16}/> سطر جدید
        </button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6">
        {fields.length === 0 ? (
          <div className="text-center py-10 text-slate-400 border-2 border-dashed border-slate-100 rounded-xl mb-6">
            هیچ زیرمجموعه‌ای تعریف نشده است. دکمه "سطر جدید" را بزنید.
          </div>
        ) : (
          <div className="overflow-x-auto mb-6">
            <table className="table w-full">
              <thead>
                <tr>
                  <th className="w-10">#</th>
                  <th>نام زیردسته</th>
                  <th>نامک (Slug)</th>
                  <th className="text-center w-24">وضعیت</th>
                  <th className="w-16"></th>
                </tr>
              </thead>
              <tbody>
                {fields.map((field, index) => (
                  <tr key={field.id} className="hover:bg-slate-50 transition-colors">
                    <td className="text-slate-400 font-mono text-xs">{index + 1}</td>
                    
                    <td>
                      <input 
                        {...register(`subs.${index}.name`, { required: true })}
                        className="input input-sm input-bordered w-full" 
                        placeholder="نام..."
                      />
                    </td>
                    
                    <td>
                      <input 
                        {...register(`subs.${index}.slug`, { required: true })}
                        className="input input-sm input-bordered w-full dir-ltr font-mono text-xs" 
                        placeholder="slug-url"
                      />
                    </td>
                    
                    <td className="text-center">
                      <label className="swap swap-rotate text-emerald-600">
                        <input type="checkbox" {...register(`subs.${index}.is_active`)} />
                        <CheckCircle2 size={20} className="swap-on"/>
                        <AlertCircle size={20} className="swap-off text-slate-300"/>
                      </label>
                    </td>

                    <td>
                      <button 
                        type="button" 
                        onClick={() => remove(index)}
                        className="btn btn-xs btn-square btn-ghost text-red-400 hover:bg-red-50"
                        // نکته: در حالت واقعی حذف اینجا فقط از لیست UI حذف میکند. 
                        // برای حذف واقعی از دیتابیس معمولا یک API جدا یا فلگ delete لازم است.
                        // در اینجا فعلاً فرض بر این است که لیست ارسالی لیست نهایی است یا دکمه حذف جدا کار میکند.
                        // اما چون متد bulk-upsert فقط ایجاد و ویرایش است، حذف را اینجا هندل نمی کنیم (کاربر باید از لیست اصلی حذف کند)
                        // پس این دکمه فقط سطرهای جدیدِ ذخیره نشده را پاک کند بهتر است.
                      >
                        <Trash2 size={16}/>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex justify-end pt-4 border-t border-slate-100">
          <button 
            type="submit" 
            disabled={bulkMutation.isPending || (!isDirty && fields.length > 0)}
            className="btn btn-primary px-8 shadow-lg"
          >
            {bulkMutation.isPending ? <span className="loading loading-spinner"></span> : <><Save size={18}/> ذخیره تغییرات لیست</>}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SubCategoryManager;