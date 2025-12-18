// src/app/features/dashboard/categories/CategoryListPage.jsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminCategoryService } from '../../services/adminCategoryService';
import { Plus, Search, Edit2, Trash2, MoreVertical, Image as ImageIcon } from 'lucide-react';
import toast from 'react-hot-toast';
import CategoryModal from './CategoryModal'; // در ادامه می‌سازیم

const CategoryListPage = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // 1. Fetch Categories
  const { data: categories = [], isLoading } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminCategoryService.getAll,
  });

  // 2. Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: adminCategoryService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-categories']);
      toast.success('دسته‌بندی با موفقیت حذف شد');
    },
    onError: () => toast.error('خطا در حذف دسته‌بندی'),
  });

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این دسته‌بندی اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const handleEdit = (category) => {
    setSelectedCategory(category);
    setIsModalOpen(true);
  };

  const handleCreate = () => {
    setSelectedCategory(null);
    setIsModalOpen(true);
  };

  // فیلتر کلاینت‌ساید (چون دیتای دسته‌بندی‌ها معمولاً کم است)
  const filteredCategories = categories.filter(cat => 
    cat.name.includes(searchTerm) || cat.slug.includes(searchTerm)
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-base-content">مدیریت دسته‌بندی‌ها</h1>
          <p className="text-sm text-base-content/60 mt-1">لیست و ویرایش دسته‌بندی‌های محصولات</p>
        </div>
        <button onClick={handleCreate} className="btn btn-primary gap-2">
          <Plus size={20} />
          افزودن دسته جدید
        </button>
      </div>

      {/* Search & Stats */}
      <div className="flex items-center gap-4 bg-base-100 p-4 rounded-xl shadow-sm border border-base-200">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-base-content/40" />
          <input 
            type="text" 
            placeholder="جستجو در نام یا نامک..." 
            className="input input-bordered w-full pr-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="text-sm text-base-content/60 hidden sm:block">
          تعداد کل: <span className="font-bold text-base-content">{categories.length}</span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto bg-base-100 rounded-xl border border-base-200 shadow-sm">
        <table className="table table-zebra w-full">
          <thead>
            <tr className="bg-base-200/50 text-base-content/70">
              <th>تصویر</th>
              <th>نام دسته</th>
              <th>نامک (Slug)</th>
              <th>دسته مادر</th>
              <th>وضعیت</th>
              <th className="text-left">عملیات</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan="6" className="text-center py-10">در حال بارگذاری...</td></tr>
            ) : filteredCategories.length === 0 ? (
              <tr><td colSpan="6" className="text-center py-10 text-base-content/50">موردی یافت نشد</td></tr>
            ) : (
              filteredCategories.map((cat) => (
                <tr key={cat.id} className="hover">
                  <td>
                    <div className="avatar">
                      <div className="w-12 h-12 rounded-lg ring-1 ring-base-200">
                        {cat.banner_box ? (
                          <img src={cat.banner_box} alt={cat.name} className="object-cover" />
                        ) : (
                          <div className="w-full h-full bg-base-200 flex items-center justify-center text-base-content/30">
                            <ImageIcon size={20} />
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="font-bold">{cat.name}</td>
                  <td className="font-mono text-xs opacity-70">{cat.slug}</td>
                  <td>
                    {cat.parent_name ? (
                      <span className="badge badge-ghost text-xs">{cat.parent_name}</span>
                    ) : (
                      <span className="text-xs opacity-40">-</span>
                    )}
                  </td>
                  <td>
                    {cat.is_active ? (
                      <span className="badge badge-success badge-sm gap-1 text-white">فعال</span>
                    ) : (
                      <span className="badge badge-error badge-sm gap-1 text-white">غیرفعال</span>
                    )}
                  </td>
                  <td>
                    <div className="flex justify-end gap-2">
                      <button 
                        onClick={() => handleEdit(cat)}
                        className="btn btn-sm btn-ghost btn-square text-info hover:bg-info/10"
                        title="ویرایش"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button 
                        onClick={() => handleDelete(cat.id)}
                        className="btn btn-sm btn-ghost btn-square text-error hover:bg-error/10"
                        title="حذف"
                      >
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

      {/* Modal */}
      {isModalOpen && (
        <CategoryModal 
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          category={selectedCategory}
          categories={categories} // پاس دادن لیست برای انتخاب والد
        />
      )}
    </div>
  );
};

export default CategoryListPage;