import React, { useState } from 'react';
import { Plus, MonitorPlay, Edit2, Trash2, Calendar, CheckCircle2, XCircle } from 'lucide-react';
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
    if (window.confirm('آیا از حذف این رسانه مطمئن هستید؟ این عمل غیرقابل بازگشت است.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleToggleStatus = (item) => {
    // تغییر سریع وضعیت بدون نیاز به باز کردن مدال (با استفاده از متد PATCH)
    updateMutation.mutate({
      id: item.id,
      data: { is_active: !item.is_active }
    });
  };

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto min-h-screen pb-32 animate-fade-in">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <div>
          <h1 className="text-2xl md:text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100">
              <MonitorPlay size={28} />
            </span>
            رسانه‌های نوار بالای سایت
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت بنرهای باریک و رسانه‌هایی که در نوار بالای سایت (Top Bar) نمایش داده می‌شوند.</p>
        </div>
        <button 
          onClick={handleOpenCreate} 
          className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12 text-base rounded-2xl"
        >
          <Plus size={20} /> افزودن رسانه
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64"><span className="loading loading-spinner loading-lg text-primary"></span></div>
      ) : mediaList.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-[2rem] border border-dashed border-slate-300">
            <div className="bg-slate-50 inline-flex p-4 rounded-full mb-4 text-slate-400">
              <MonitorPlay size={48}/>
            </div>
            <h3 className="text-lg font-bold text-slate-600">هیچ رسانه‌ای یافت نشد</h3>
            <p className="text-slate-400 mt-1">با کلیک روی دکمه افزودن، اولین بنر نوار بالای سایت را ایجاد کنید.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {mediaList.map((media) => (
            <div key={media.id} className={`group bg-white rounded-3xl border ${media.is_active ? 'border-indigo-100' : 'border-slate-100'} shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col relative`}>
              
              {/* Status Badge */}
              <div className="absolute top-3 right-3 z-10">
                 {media.is_active ? (
                    <span className="badge badge-success gap-1 py-3 px-3 shadow-lg bg-emerald-500 border-none text-white font-medium text-xs">
                        <CheckCircle2 size={14}/> فعال
                    </span>
                 ) : (
                    <span className="badge gap-1 py-3 px-3 shadow-lg bg-slate-600 border-none text-white font-medium text-xs">
                        <XCircle size={14}/> غیرفعال
                    </span>
                 )}
              </div>

              {/* Image Area */}
              <div className="relative h-32 bg-slate-100 overflow-hidden flex items-center justify-center p-2">
                {/* چون معمولا بنر نوار بالا خیلی باریک است، استایل object-contain ممکن است بهتر باشد */}
                <img 
                    src={media.file_url} 
                    alt="Site Media" 
                    className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100 gap-2 backdrop-blur-[1px]">
                    <button 
                        onClick={() => handleOpenEdit(media)}
                        className="btn btn-sm btn-circle bg-white border-none hover:bg-slate-200 text-blue-600 shadow-lg"
                        title="ویرایش"
                    >
                        <Edit2 size={16}/>
                    </button>
                    <button 
                        onClick={() => handleDelete(media.id)}
                        className="btn btn-sm btn-circle bg-white border-none hover:bg-slate-200 text-red-500 shadow-lg"
                        title="حذف"
                    >
                        <Trash2 size={16}/>
                    </button>
                </div>
              </div>

              {/* Info Area & Quick Actions */}
              <div className="p-5 bg-slate-50/50 flex-1 flex items-center justify-between border-t border-slate-100">
                 <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
                     <Calendar size={14} className="text-slate-400"/>
                     <span>{new Date(media.created_at).toLocaleDateString('fa-IR')}</span>
                 </div>
                 
                 <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-600">وضعیت نمایش:</span>
                    <input 
                        type="checkbox" 
                        className="toggle toggle-sm toggle-success" 
                        checked={media.is_active}
                        onChange={() => handleToggleStatus(media)}
                        disabled={updateMutation.isPending}
                    />
                 </div>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Modal Form */}
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