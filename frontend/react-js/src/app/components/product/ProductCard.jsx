// src/app/components/product/ProductCard.jsx
import { Link } from 'react-router-dom';
import { Eye } from 'lucide-react';

const ProductCard = ({ product }) => {
  const formattedPrice = new Intl.NumberFormat('fa-IQ').format(parseFloat(product.price) || 0);

  // استخراج نام دسته‌ها (با پشتیبانی از حالت‌های بدون دسته مثل لندینگ)
  const parentCategory = product.category?.parent_category || 'محصولات';
  const childCategory = product.category?.children_category;

  // دریافت آدرس عکس با پشتیبانی از هر دو حالت API (شاپ و لندینگ)
  const imageUrl = product.thumbnail || product.image;

  return (
    <Link 
      to={`/product/${product.slug}`} 
      className="group bg-white rounded-[24px] p-2 border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 h-full flex flex-col block"
    >
      
      {/* بخش تصویر */}
      <div className="relative aspect-video rounded-2xl bg-slate-50 overflow-hidden isolate">
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
             تصویر ندارد
          </div>
        )}

        {/* دکمه مخفی هاور */}
        <div className="absolute inset-0 bg-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[1px]">
           <button className="btn btn-sm btn-primary glass text-white rounded-full px-5 font-bold shadow-lg text-xs">
            <Eye size={14} className="mr-1" />
            مشاهده
           </button>
        </div>
      </div>

      {/* بخش اطلاعات */}
      <div className="pt-3 px-2 flex flex-col gap-1.5 flex-1">
        
        {/* مسیر دسته‌بندی */}
        <div className="text-[10px] text-gray-400 font-medium flex items-center gap-1 truncate" dir="rtl">
           <span className="hover:text-primary transition-colors">
             {parentCategory}
           </span>
           
           {childCategory && (
             <>
               <span className="text-[8px] opacity-60">❮</span>
               <span className="text-gray-500 hover:text-primary transition-colors">
                 {childCategory}
               </span>
             </>
           )}
        </div>

        {/* نام محصول */}
        <h3 className="text-sm font-bold text-slate-800 leading-snug line-clamp-1 group-hover:text-primary transition-colors">
          {product.name}
        </h3>

        {/* قیمت */}
        <div className="mt-auto flex items-center justify-end text-emerald-600 gap-1">
          <span className="text-lg font-black tracking-tight">{formattedPrice}</span>
          <span className="text-[10px] font-bold opacity-80 pt-1">IQD</span>
        </div>

      </div>
    </Link>
  );
};

export default ProductCard;