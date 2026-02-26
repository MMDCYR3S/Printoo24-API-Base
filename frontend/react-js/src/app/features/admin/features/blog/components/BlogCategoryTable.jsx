import React, { useState } from 'react';
import { useBlogCategories, useDeleteBlogCategory, useBulkDeleteBlogCategories } from '../hooks/useBlogCategories';
import BlogCategoryModal from './components/BlogCategoryModal';

const BlogCategoriesPage = () => {
  const { data: categories, isLoading, isError } = useBlogCategories();
  const deleteMutation = useDeleteBlogCategory();
  const bulkDeleteMutation = useBulkDeleteBlogCategories();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editData, setEditData] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);

  const handleOpenModal = (data = null) => {
    setEditData(data);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setEditData(null);
    setIsModalOpen(false);
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این دسته‌بندی مطمئن هستید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const handleBulkDelete = () => {
    if (window.confirm('آیا از حذف موارد انتخاب شده مطمئن هستید؟')) {
      bulkDeleteMutation.mutate(selectedIds, {
        onSuccess: () => setSelectedIds([]) // پاک کردن انتخاب‌ها بعد از حذف موفق
      });
    }
  };

  if (isLoading) return <div className="p-6 text-center">در حال بارگذاری...</div>;
  if (isError) return <div className="p-6 text-center text-red-500">خطا در دریافت اطلاعات</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">مدیریت دسته‌بندی‌های بلاگ</h1>
        <button
          onClick={() => handleOpenModal()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          + افزودن دسته جدید
        </button>
      </div>

      {/* نوار عملیات گروهی */}
      {selectedIds.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg mb-4 flex justify-between items-center">
          <span className="text-sm text-blue-800 font-medium">
            {selectedIds.length} مورد انتخاب شده
          </span>
          <div className="flex gap-2">
             {/* دکمه‌های تغییر وضعیت گروهی هم اینجا می‌تواند اضافه شود */}
            <button
              onClick={handleBulkDelete}
              className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
            >
              حذف گروهی
            </button>
          </div>
        </div>
      )}

      {/* جدول داده‌ها */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                انتخاب
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">شناسه</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نام</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نامک (Slug)</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">وضعیت</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">عملیات</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {categories?.map((cat) => (
              <tr key={cat.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(cat.id)}
                    onChange={() => toggleSelect(cat.id)}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{cat.id}</td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{cat.name}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{cat.slug}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${cat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {cat.is_active ? 'فعال' : 'غیرفعال'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-medium flex gap-3">
                  <button
                    onClick={() => handleOpenModal(cat)}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    ویرایش
                  </button>
                  <button
                    onClick={() => handleDelete(cat.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    حذف
                  </button>
                </td>
              </tr>
            ))}
            {categories?.length === 0 && (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                  هیچ دسته‌بندی یافت نشد.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <BlogCategoryModal 
        isOpen={isModalOpen} 
        onClose={handleCloseModal} 
        editData={editData} 
      />
    </div>
  );
};

export default BlogCategoriesPage;