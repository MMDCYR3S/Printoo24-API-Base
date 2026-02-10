import React from 'react';
import { Trash2, UploadCloud, CheckCircle, Plus, ImageIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

const CartItem = ({ item, onDelete, isDeleting }) => {
  const specs = item.items || {}; 
  const uploads = item.uploads || [];
  const hasUpload = uploads.length > 0;
  
  // استخراج تصویر از آبجکت پروداکت
  const productImage = item.product?.image;

  return (
    <div className="bg-white border border-slate-100 rounded-2xl p-4 sm:p-6 mb-4 shadow-sm hover:shadow-md transition-shadow relative group">
      
      <div className="flex flex-col sm:flex-row gap-6">
        
        {/* --- بخش تصویر محصول (جدید) --- */}
        <div className="shrink-0">
          <div className="w-full sm:w-28 h-28 bg-slate-100 rounded-xl overflow-hidden border border-slate-200">
            {productImage ? (
              <img 
                src={productImage} 
                alt={item.product?.name || item.name} 
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-300">
                <ImageIcon size={32} />
              </div>
            )}
          </div>
        </div>

        {/* بخش اطلاعات محصول */}
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-slate-800 mb-1 line-clamp-1">
                {item.product?.name || item.name}
              </h3>
              <div className="flex items-center gap-2 text-xs text-slate-400 font-mono mb-4">
                <span>CODE: {item.product?.slug}</span>
              </div>
            </div>
            
            <button 
              onClick={() => onDelete(item.id)}
              disabled={isDeleting}
              className="sm:hidden text-slate-300 hover:text-red-500 transition-colors p-2"
            >
              <Trash2 size={18} />
            </button>
          </div>

          <div className="bg-slate-50 rounded-xl p-4 grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-8 text-sm">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2 md:border-0 md:pb-0">
              <span className="text-slate-500">سایز:</span>
              <span className="font-medium text-slate-700">{specs.size_label}</span>
            </div>

            <div className="flex items-center justify-between border-b border-slate-200 pb-2 md:border-0 md:pb-0">
              <span className="text-slate-500">تعداد:</span>
              <span className="font-medium text-slate-700">
                {item.quantity.toLocaleString()} عدد
              </span>
            </div>

            {specs.dimensions && specs.dimensions !== "0.0x0.0" && (
              <div className="flex items-center justify-between text-blue-600">
                <span className="opacity-70">ابعاد دقیق:</span>
                <span className="font-mono dir-ltr">{specs.dimensions}</span>
              </div>
            )}

            {specs.options?.map((opt, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-slate-500">{opt.option_label}:</span>
                <span className="font-medium text-slate-700">{opt.value?.label}</span>
              </div>
            ))}
          </div>

          {/* بخش وضعیت فایل طراحی */}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {hasUpload ? (
              <>
                 <div className="flex items-center gap-2 text-xs font-medium text-emerald-600 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-100">
                    <CheckCircle size={14} />
                    <span>{uploads.length} فایل آپلود شده</span>
                 </div>
                 {/* دکمه افزودن فایل بیشتر */}
                 <Link 
                   to={`/cart/upload/${item.id}`}
                   className="flex items-center gap-1 text-xs text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors"
                 >
                   <Plus size={14} />
                   مدیریت / افزودن فایل
                 </Link>
              </>
            ) : (
              <div className="flex items-center gap-2 w-full sm:w-auto">
                 <Link 
                   to={`/cart/upload/${item.id}`}
                   className="flex items-center justify-center gap-2 text-xs font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 px-4 py-2 rounded-lg border border-slate-200 transition-colors flex-1 sm:flex-none"
                 >
                   <UploadCloud size={14} />
                   آپلود فایل طراحی (اختیاری)
                 </Link>
              </div>
            )}
          </div>
        </div>

        {/* بخش قیمت و حذف (دسکتاپ) */}
        <div className="flex flex-col justify-between items-end min-w-[140px] border-t sm:border-t-0 border-slate-100 pt-4 sm:pt-0 mt-4 sm:mt-0">
          <div className="text-left">
            <span className="block text-xs text-slate-400 mb-1">قیمت کل آیتم</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-black text-slate-800 tracking-tight">
                {parseFloat(item.price).toLocaleString()}
              </span>
              <span className="text-xs text-slate-500">تومان</span>
            </div>
          </div>

          <button 
            onClick={() => onDelete(item.id)}
            disabled={isDeleting}
            className="hidden sm:flex items-center gap-2 text-slate-400 hover:text-red-600 hover:bg-red-50 px-3 py-2 rounded-lg transition-all text-sm mt-4"
          >
            <Trash2 size={16} />
            <span>حذف آیتم</span>
          </button>
        </div>

      </div>
    </div>
  );
};

export default CartItem;