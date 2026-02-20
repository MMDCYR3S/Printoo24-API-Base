import React, { useState } from 'react';
import { Box, Trash2, Upload, Ruler, PenTool, Layers, FileText, ExternalLink, Image as ImageIcon } from 'lucide-react';
import { useAdminOrderDetails } from '../../../../hooks/useAdminOrderDetails';
import { formatPrice } from '../../../../utils/formatPrice';
import { apiClient } from '../../../../../../services/apiClient';

// === Helper Functions ===
const getAbsoluteUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  try {
    const axiosBaseUrl = apiClient.defaults.baseURL; 
    const origin = new URL(axiosBaseUrl).origin;
    return `${origin}/${url.replace(/^\//, '')}`;
  } catch (error) {
    return url;
  }
};

const isImageFile = (url) => {
  if (!url) return false;
  return /\.(jpeg|jpg|gif|png|webp|svg|bmp)$/i.test(url);
};


const OrderItemsList = ({ order }) => {
  const { deleteItemMutation, uploadFileMutation } = useAdminOrderDetails();
  const [uploadingItemId, setUploadingItemId] = useState(null);

  const handleDeleteItem = (itemId) => {
    if (window.confirm('آیا از حذف این ردیف کالا از سفارش مطمئن هستید؟ (مبلغ کل سفارش باید دستی اصلاح شود)')) {
      deleteItemMutation.mutate(itemId);
    }
  };

  const handleFileUpload = (itemId, e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    
    setUploadingItemId(itemId);
    uploadFileMutation.mutate(
      { itemId, formData },
      { onSettled: () => setUploadingItemId(null) }
    );
  };

  const renderSpecificationsList = (specs) => {
    if (!specs) return <span className="text-slate-400 text-sm">مشخصاتی ثبت نشده است</span>;

    return (
      <div className="space-y-3">
        {(specs.width || specs.height) && (
          <div className="flex items-center justify-between pb-2 border-b border-slate-200/60 last:border-0 last:pb-0">
            <div className="flex items-center gap-2 text-slate-500">
               <Ruler size={16} />
               <span className="text-sm font-medium">ابعاد (طول × عرض)</span>
            </div>
            <span className="text-sm font-bold text-slate-800 dir-ltr">{specs.width || '?'} × {specs.height || '?'} cm</span>
          </div>
        )}

        {specs.has_design && (
          <div className="flex items-center justify-between pb-2 border-b border-slate-200/60 last:border-0 last:pb-0">
            <div className="flex items-center gap-2 text-primary">
               <PenTool size={16} />
               <span className="text-sm font-bold">وضعیت طراحی</span>
            </div>
            <span className="text-xs font-bold text-primary bg-primary/10 px-2.5 py-1 rounded-md">نیاز به طراحی</span>
          </div>
        )}

        {specs.options && Array.isArray(specs.options) && specs.options.map((opt, idx) => (
          <div key={idx} className="flex items-center justify-between pb-2 border-b border-slate-200/60 last:border-0 last:pb-0">
            <div className="flex items-center gap-2 text-slate-500">
               <Layers size={16} />
               <span className="text-sm font-medium">{opt.name}</span>
            </div>
            <span className="text-sm font-bold text-slate-800">{opt.value}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* --- هدر اصلی بخش --- */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-3">
          <div className="p-2 bg-slate-800 rounded-lg text-white shadow-sm">
            <Box size={20} />
          </div>
          اقلام سفارش
        </h2>
        <div className="bg-slate-100 text-slate-600 font-bold px-3 py-1 rounded-md text-sm">
          {order.items?.length || 0} ردیف
        </div>
      </div>

      {/* --- لیست محصولات --- */}
      <div className="grid grid-cols-1 gap-6">
        {order.items?.map((item, index) => (
          <div key={item.id} className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all">
            
            {/* نوار عنوان محصول */}
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex flex-wrap justify-between items-center gap-4">
               <div className="flex items-center gap-3">
                  <span className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-200 text-slate-600 font-bold text-sm">
                    {index + 1}
                  </span>
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{item.product_name}</h3>
                    <p className="text-slate-400 font-mono text-xs mt-0.5">SLUG: {item.product_slug}</p>
                  </div>
               </div>
               <div className="bg-white border border-slate-200 text-slate-700 px-4 py-1.5 rounded-lg font-bold text-sm shadow-sm">
                  تعداد: {item.quantity}
               </div>
            </div>

            {/* بدنه اصلی کارت */}
            <div className="p-6">
              <div className="flex flex-col lg:flex-row gap-8">
                
                {/* بخش راست: مشخصات فنی (بخش وسیع‌تر) */}
                <div className="flex-1 space-y-3">
                   <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">مشخصات فنی</h4>
                   <div className="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                     {renderSpecificationsList(item.specifications)}
                   </div>
                </div>

                {/* بخش چپ: قیمت و عملیات (بخش جمع‌وجورتر) */}
                <div className="w-full lg:w-72 flex flex-col gap-5">
                   
                   {/* باکس قیمت */}
                   <div className="space-y-3">
                     <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">مبلغ ردیف</h4>
                     <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100 flex items-center justify-between">
                       <span className="text-emerald-700 font-black text-xl dir-ltr tracking-tight">
                         {formatPrice(item.price)}
                       </span>
                       <span className="text-emerald-600/70 font-bold text-xs">IQD</span>
                     </div>
                   </div>

                   {/* باکس عملیات */}
                   <div className="space-y-3">
                     <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">عملیات</h4>
                     <div className="flex flex-col gap-2">
                       {/* دکمه آپلود */}
                       <label className={`btn w-full rounded-xl h-11 min-h-[2.75rem] text-sm font-bold shadow-sm ${uploadingItemId === item.id ? 'btn-disabled bg-slate-100' : 'bg-primary hover:bg-primary-focus text-white border-0'}`}>
                         <input type="file" className="hidden" onChange={(e) => handleFileUpload(item.id, e)} disabled={uploadingItemId === item.id} />
                         {uploadingItemId === item.id ? (
                           <span className="loading loading-spinner loading-sm"></span>
                         ) : (
                           <><Upload size={18} /> آپلود فایل طراحی</>
                         )}
                       </label>

                       {/* دکمه حذف */}
                       <button 
                         onClick={() => handleDeleteItem(item.id)}
                         className="btn w-full rounded-xl h-11 min-h-[2.75rem] bg-white border border-slate-200 text-error hover:bg-error hover:text-white hover:border-error transition-colors shadow-sm text-sm font-bold" 
                       >
                         <Trash2 size={18} /> حذف این ردیف
                       </button>
                     </div>
                   </div>

                </div>
              </div>

              {/* گالری پیوست‌ها */}
              {item.files && item.files.length > 0 && (
                <div className="mt-6 pt-6 border-t border-slate-100">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <ImageIcon size={16} /> پیوست‌های آپلود شده
                  </h4>
                  
                  <div className="flex flex-wrap gap-3">
                    {item.files.map((file) => {
                      const absoluteUrl = getAbsoluteUrl(file.file_url);
                      const isImage = isImageFile(file.file_url);

                      return (
                        <a 
                          key={file.id} 
                          href={absoluteUrl} 
                          target="_blank" 
                          rel="noreferrer"
                          className="group relative w-24 h-24 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden flex flex-col items-center justify-center shadow-sm hover:shadow-md transition-all shrink-0"
                        >
                          {isImage ? (
                            <img 
                              src={absoluteUrl} 
                              alt="پیوست" 
                              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                              onError={(e) => { e.target.style.display = 'none'; }} 
                            />
                          ) : (
                            <div className="flex flex-col items-center gap-1.5">
                              <FileText size={24} className="text-slate-300 group-hover:text-primary transition-colors" />
                              <span className="text-[10px] font-bold text-slate-400 group-hover:text-primary">فایل</span>
                            </div>
                          )}

                          <div className="absolute inset-0 bg-slate-900/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[2px]">
                            <ExternalLink size={20} className="text-white drop-shadow-lg" />
                          </div>
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}

            </div>
          </div>
        ))}

        {/* حالت بدون آیتم */}
        {(!order.items || order.items.length === 0) && (
          <div className="text-center py-16 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
            <Box size={40} className="mx-auto text-slate-300 mb-3" />
            <p className="text-slate-500 font-bold text-lg">این سفارش فاقد آیتم است.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderItemsList;