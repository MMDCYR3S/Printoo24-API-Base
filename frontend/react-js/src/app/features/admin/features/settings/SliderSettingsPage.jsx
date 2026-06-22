// src/app/features/settings/SliderSettingsPage.jsx
import React, { useState } from 'react';
import { Plus, Image as ImageIcon, Edit2, Trash2, Calendar } from 'lucide-react';
import { useAdminSliders } from './hooks/useAdminSliders';
import SliderModal from './components/SliderModal';

const SliderSettingsPage = () => {
  const { sliders, isLoading, createMutation, updateMutation, deleteMutation } = useAdminSliders();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Open Create
  const handleOpenCreate = () => {
    setEditingItem(null);
    setIsModalOpen(true);
  };

  // Open Edit
  const handleOpenEdit = (item) => {
    setEditingItem(item);
    setIsModalOpen(true);
  };

  // Submit Handler
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

  // Delete Handler
  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این اسلایدر مطمئن هستید؟')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto min-h-screen pb-32 animate-fade-in">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl border border-indigo-100"><ImageIcon size={28} /></span>
            اسلایدرهای صفحه اصلی
          </h1>
          <p className="text-slate-500 mt-2 text-sm">مدیریت بنرهای تبلیغاتی و اسلایدرهای بالای سایت</p>
        </div>
        <button 
          onClick={handleOpenCreate} 
          className="btn btn-primary px-6 shadow-lg shadow-primary/30 h-12 text-base"
        >
          <Plus size={20} /> افزودن اسلایدر
        </button>
      </div>

      {/* Grid Content */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64"><span className="loading loading-spinner loading-lg text-primary"></span></div>
      ) : sliders.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-[2rem] border border-dashed border-slate-300">
            <div className="bg-slate-50 inline-flex p-4 rounded-full mb-4 text-slate-400"><ImageIcon size={48}/></div>
            <h3 className="text-lg font-bold text-slate-600">هنوز اسلایدری ندارید</h3>
            <p className="text-slate-400 mt-1">با دکمه بالا اولین اسلایدر خود را ایجاد کنید.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {sliders.map((slider) => (
            <div key={slider.id} className="group bg-white rounded-3xl border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden flex flex-col">
              
              {/* Image Area */}
              <div className="relative aspect-[2/1] bg-slate-100 overflow-hidden">
                <img 
                    src={slider.image_url} 
                    alt={slider.name} 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100 gap-2">
                    <button 
                        onClick={() => handleOpenEdit(slider)}
                        className="btn btn-sm btn-circle bg-white/90 border-none hover:bg-white text-blue-600 shadow-lg"
                    >
                        <Edit2 size={16}/>
                    </button>
                    <button 
                        onClick={() => handleDelete(slider.id)}
                        className="btn btn-sm btn-circle bg-white/90 border-none hover:bg-white text-red-500 shadow-lg"
                    >
                        <Trash2 size={16}/>
                    </button>
                </div>
              </div>

              {/* Info Area */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                 <div>
                    <h3 className="font-bold text-slate-800 text-lg mb-1 line-clamp-1">{slider.name}</h3>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mt-2">
                        <Calendar size={14}/>
                        <span>ایجاد: {new Date(slider.created_at).toLocaleDateString('EN')}</span>
                    </div>
                 </div>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <SliderModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        editData={editingItem}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

    </div>
  );
};

export default SliderSettingsPage;