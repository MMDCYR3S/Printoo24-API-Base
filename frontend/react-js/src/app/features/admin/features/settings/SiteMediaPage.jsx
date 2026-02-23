import React, { useState } from 'react';
import { Plus, MonitorPlay, Edit2, Trash2, Calendar, Link as LinkIcon } from 'lucide-react';
import { useAdminMedia } from './hooks/useAdminMedia';
import MediaModal from './components/MediaModal';

const SiteMediaPage = () => {
  const { mediaList, isLoading, createMutation, updateMutation, deleteMutation } = useAdminMedia();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const handleOpenCreate = () => {
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (item) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleSubmit = (data) => {
    if (editingItem) {
      updateMutation.mutate(
        { id: editingItem.id, data },
        { onSuccess: () => setIsModalOpen(false) }
      );
    } else {
      createMutation.mutate(data, {
        onSuccess: () => setIsModalOpen(false)
      });
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این رسانه مطمئن هستید؟ این عملیات برگشت‌پذیر نیست.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleToggleStatus = (item) => {
    updateMutation.mutate({
      id: item.id,
      data: { is_active: !item.is_active }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto min-h-screen pb-32 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100">
              <MonitorPlay size={28} />
            </span>
            رسانه‌های نوار بالای سایت
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت بنرهای تبلیغاتی و گیف‌های بالای هدر.</p>
        </div>
        <button 
          onClick={handleOpenCreate} 
          className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12 text-base rounded-2xl"
        >
          <Plus size={20} /> آپلود رسانه جدید
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64"><span className="loading loading-spinner loading-lg text-primary"></span></div>
      ) : (!mediaList || mediaList.length === 0) ? (
        <div className="text-center py-20 bg-white rounded-[2rem] border border-dashed border-slate-300">
            <div className="bg-slate-50 inline-flex p-4 rounded-full mb-4 text-slate-400">
              <MonitorPlay size={48}/>
            </div>
            <h3 className="text-lg font-bold text-slate-600">هیچ رسانه‌ای یافت نشد</h3>
            <p className="text-slate-400 mt-1">اولین بنر خود را با دکمه بالا آپلود کنید.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {mediaList.map((media) => (
            <div key={media.id} className={`group bg-white rounded-3xl border ${media.is_active ? 'border-indigo-500 ring-2 ring-indigo-50' : 'border-slate-100'} shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col relative`}>
              
              {/* Badge */}
              <div className="absolute top-3 right-3 z-10">
                 {media.is_active ? (
                    <span className="badge badge-success gap-1 py-3 px-3 shadow-lg bg-emerald-500 border-none text-white font-medium text-xs">فعال</span>
                 ) : (
                    <span className="badge gap-1 py-3 px-3 shadow-lg bg-slate-600 border-none text-white font-medium text-xs">غیرفعال</span>
                 )}
              </div>

              {/* Image Preview */}
              <div className="relative h-40 bg-slate-50 overflow-hidden flex items-center justify-center p-2">
                <img 
                    src={media.file} 
                    alt="Banner" 
                    className="w-full h-full object-contain transition-transform duration-500"
                />
              </div>

              {/* Link Indicator */}
              {media.link && (
                 <div className="px-4 pt-3 flex items-center gap-2 text-xs text-blue-600 bg-white">
                    <LinkIcon size={14} />
                    <a href={media.link} target="_blank" rel="noreferrer" className="truncate hover:underline" dir="ltr">
                        {media.link}
                    </a>
                 </div>
              )}

              {/* Action Bar */}
              <div className="p-4 mt-auto bg-white flex items-center justify-between border-t border-slate-100">
                 <div className="flex items-center gap-3">
                    <input 
                        type="checkbox" 
                        className="toggle toggle-sm toggle-success" 
                        checked={media.is_active}
                        onChange={() => handleToggleStatus(media)}
                        disabled={updateMutation.isPending}
                        title="تغییر وضعیت"
                    />
                    <span className="text-xs font-bold text-slate-500">
                        {new Date(media.created_at).toLocaleDateString('fa-IR')}
                    </span>
                 </div>
                 
                 <div className="flex items-center gap-1">
                    <button 
                        onClick={() => handleOpenEdit(media)}
                        className="btn btn-sm btn-circle btn-ghost text-blue-600 bg-blue-50 hover:bg-blue-100"
                        title="ویرایش"
                    >
                        <Edit2 size={16}/>
                    </button>
                    <button 
                        onClick={() => handleDelete(media.id)}
                        className="btn btn-sm btn-circle btn-ghost text-red-500 bg-red-50 hover:bg-red-100"
                        title="حذف"
                    >
                        <Trash2 size={16}/>
                    </button>
                 </div>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <MediaModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        editData={editingItem}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />
    </div>
  );
};

export default SiteMediaPage;