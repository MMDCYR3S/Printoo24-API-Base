// src/app/features/settings/ModalSettingsPage.jsx
import React, { useState } from 'react';
import { Plus, MessageSquare, Edit2, Trash2, Link as LinkIcon, Eye, EyeOff } from 'lucide-react';
import { useAdminModals } from './hooks/useAdminModals';
import ModalForm from './components/ModalForm';
import clsx from 'clsx';

const ModalSettingsPage = () => {
  const { modals, isLoading, createMutation, updateMutation, deleteMutation, toggleStatusMutation } = useAdminModals();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const handleCreate = () => {
    setEditingItem(null);
    setIsModalOpen(true);
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  const handleSubmit = (data) => {
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data }, { onSuccess: () => setIsModalOpen(false) });
    } else {
      createMutation.mutate(data, { onSuccess: () => setIsModalOpen(false) });
    }
  };

  const handleDelete = (id) => {
    if (window.confirm('آیا مطمئن هستید؟')) deleteMutation.mutate(id);
  };

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto min-h-screen pb-32 animate-fade-in">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-rose-50 text-rose-600 rounded-2xl border border-rose-100"><MessageSquare size={28} /></span>
            مودال‌های اطلاع‌رسانی
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت پاپ‌آپ‌ها و پیام‌های تبلیغاتی سایت</p>
        </div>
        <button onClick={handleCreate} className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12">
          <Plus size={20} /> مودال جدید
        </button>
      </div>

      {/* Grid Content */}
      {isLoading ? (
        <div className="flex justify-center h-64"><span className="loading loading-spinner loading-lg text-primary"></span></div>
      ) : modals.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
             <div className="bg-slate-50 inline-flex p-4 rounded-full mb-4 text-slate-400"><MessageSquare size={40}/></div>
             <p className="text-slate-500 font-bold">هیچ مودالی تعریف نشده است.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
          {modals.map((modal) => (
            <div key={modal.id} className={clsx("relative bg-white rounded-3xl border shadow-sm flex flex-col overflow-hidden transition-all hover:shadow-xl group", modal.is_active ? "border-slate-100" : "border-slate-100 opacity-80 grayscale-[0.5] hover:grayscale-0")}>
              
              {/* Status Badge */}
              <div className="absolute top-3 right-3 z-10">
                 <button 
                    onClick={(e) => { e.stopPropagation(); toggleStatusMutation.mutate(modal.id); }}
                    className={clsx("badge border-0 gap-1 py-3 px-3 cursor-pointer shadow-sm transition-transform active:scale-95 font-bold", 
                        modal.is_active ? "bg-emerald-500 text-white" : "bg-slate-200 text-slate-500"
                    )}
                 >
                    {modal.is_active ? <><Eye size={14}/> فعال</> : <><EyeOff size={14}/> غیرفعال</>}
                 </button>
              </div>

              {/* Image Preview */}
              <div className="aspect-[4/3] bg-slate-50 relative border-b border-slate-50">
                {modal.image_url ? (
                    <img src={modal.image_url} alt={modal.title} className="w-full h-full object-cover" />
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-300"><MessageSquare size={48}/></div>
                )}
              </div>

              {/* Content */}
              <div className="p-5 flex-1 flex flex-col">
                <h3 className="font-bold text-slate-800 text-lg mb-2">{modal.title}</h3>
                <p className="text-slate-500 text-sm line-clamp-2 mb-4 flex-1">{modal.description || 'بدون توضیحات'}</p>
                
                {modal.cta_text && (
                    <div className="flex items-center gap-2 text-xs text-blue-600 bg-blue-50 p-2 rounded-lg mb-4 w-fit">
                        <LinkIcon size={14}/>
                        <span className="font-bold">{modal.cta_text}</span>
                    </div>
                )}

                <div className="flex gap-2 mt-auto pt-4 border-t border-slate-100">
                    <button onClick={() => handleEdit(modal)} className="btn btn-sm btn-ghost flex-1 text-slate-600 hover:bg-blue-50 hover:text-blue-600">
                        <Edit2 size={16}/> ویرایش
                    </button>
                    <button onClick={() => handleDelete(modal.id)} className="btn btn-sm btn-ghost text-red-400 hover:bg-red-50 hover:text-red-500 px-3">
                        <Trash2 size={16}/>
                    </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Form */}
      <ModalForm 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)}
        editData={editingItem}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />
    </div>
  );
};

export default ModalSettingsPage;