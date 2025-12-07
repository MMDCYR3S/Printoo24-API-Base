// src/app/components/product/ProductCard.jsx
import { ShoppingCart, Eye, Hash } from 'lucide-react';

const ProductCard = ({ product }) => {
  const formattedPrice = new Intl.NumberFormat('fa-IQ').format(product.price || 0);

  return (
    <div className="group relative bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 w-full h-full flex flex-col overflow-hidden">
      
      {/* بخش تصویر با دکمه‌های مخفی */}
      <div className="relative aspect-[16/9] bg-slate-100 overflow-hidden">
        {product.image ? (
          <img 
            src={product.image} 
            alt={product.name} 
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            onError={(e) => { e.target.src = 'https://via.placeholder.com/400x225?text=No+Image'; }}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-slate-300">
             <span className="text-xs">بدون تصویر</span>
          </div>
        )}

        {/* لایه تاریک روی عکس در حالت هاور */}
        <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2 backdrop-blur-[2px]">
           <button className="btn btn-sm btn-circle btn-primary text-white shadow-lg tooltip tooltip-top" data-tip="افزودن">
             <ShoppingCart size={16} />
           </button>
           <button className="btn btn-sm btn-circle btn-ghost bg-white/20 text-white hover:bg-white hover:text-slate-900 backdrop-blur-md shadow-lg tooltip tooltip-top" data-tip="مشاهده">
             <Eye size={16} />
           </button>
        </div>

        {/* بج "تحویل فوری" یا "جدید" (مثال) */}
        <div className="absolute top-2 right-2">
           <span className="badge badge-xs bg-emerald-500 border-none text-white shadow-sm px-2 py-2">فوری</span>
        </div>
      </div>

      {/* بدنه کارت */}
      <div className="p-3 flex flex-col flex-1 gap-2">

        {/* عنوان */}
        <h3 className="text-sm font-bold text-slate-700 leading-snug line-clamp-2 group-hover:text-primary transition-colors ">
          {product.name}
        </h3>

        {/* خط جداکننده */}
        <div className="border-t border-slate-200 my-auto"></div>

        {/* قیمت و واحد */}

          <div className="flex flex-col">
            <div className="flex items-baseline gap-1">
              <span className="text-lg font-black text-emerald-600">{formattedPrice}</span>
              <span className="text-[10px] text-emerald-700 font-bold">IQD</span>
            </div>
          </div>


      </div>
    </div>
  );
};

export default ProductCard;