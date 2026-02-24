// src/app/components/product/ProductCard.jsx
import { Link } from 'react-router-dom';
import { Eye, PhoneCall } from 'lucide-react';
import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const ProductCard = ({ product }) => {
  // استفاده از show_price و فرمت کردن آن
  const formattedPrice = new Intl.NumberFormat('fa-IR').format(parseFloat(product.show_price) || 0);

  // استخراج نام دسته‌ها با هندل کردن حالت‌های null به صورت ایمن
  const parentCategory = product.category?.parent_category || 'بدون دسته‌بندی';
  const childCategory = product.category?.children_category;

  // دریافت تصویر (با فال‌بک امن)
  const imageUrl = product.thumbnail;

  return (
    <Link 
      to={`/shop/detail/${product.slug}`} // آپدیت شده بر اساس فرمت استاندارد
      className="group border border-slate-200 rounded-[24px] bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-300 h-full flex flex-col block overflow-hidden"
    >
      {/* بخش تصویر */}
      <div className="relative aspect-video bg-slate-50 overflow-hidden isolate">
        {imageUrl ? (
          <img 
            src={imageUrl} 
            alt={product.name} 
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            onError={(e) => { e.target.src = 'https://via.placeholder.com/400x225?text=No+Image'; }}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-300 text-xs font-medium">
             بدون تصویر
          </div>
        )}

        {/* دکمه مخفی هاور */}
        <div className="absolute inset-0 bg-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[1px]">
           <button className="flex items-center gap-1 bg-primary text-white rounded-full px-5 py-2 font-bold shadow-lg text-xs hover:bg-primary-focus transition-colors">
            <Eye size={16} />
            مشاهده
           </button>
        </div>
      </div>

      {/* بخش اطلاعات */}
      <div className="pt-4 pb-4 px-4 flex flex-col gap-2 flex-1">
        
        {/* مسیر دسته‌بندی */}
        <div className="text-[10px] text-slate-400 font-medium flex items-center gap-1 truncate" dir="rtl">
           <span className="hover:text-primary transition-colors">
             {parentCategory}
           </span>
           
           {childCategory && (
             <>
               <span className="text-[8px] opacity-60">❮</span>
               <span className="text-slate-500 hover:text-primary transition-colors truncate">
                 {childCategory}
               </span>
             </>
           )}
        </div>

        {/* نام محصول */}
        <h3 className="text-sm font-bold text-slate-800 leading-snug line-clamp-2 group-hover:text-primary transition-colors">
          {product.name}
        </h3>

        {/* بخش قیمت‌گذاری بر اساس منطق جدید */}
        <div className="mt-auto pt-3 flex items-center justify-end">
          {product.has_price ? (
            <div className="flex items-center text-emerald-600 gap-1">
              <span className="text-lg font-black tracking-tight">{formattedPrice}</span>
              <span className="text-[10px] font-bold opacity-80 pt-1">{globalText.currency || 'تومان'}</span>
            </div>
          ) : (
            <div className="w-full flex items-center justify-center gap-1.5 bg-amber-50 text-amber-600 rounded-xl py-2 px-3 border border-amber-100">
              <PhoneCall size={14} />
              <span className="text-xs font-bold">استعلام قیمت</span>
            </div>
          )}
        </div>

      </div>
    </Link>
  );
};

export default ProductCard;