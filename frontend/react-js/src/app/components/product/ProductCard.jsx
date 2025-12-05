// src/app/components/product/ProductCard.jsx
import { ImageOff } from 'lucide-react';

const ProductCard = ({ product }) => {
  // فرمت‌بندی قیمت
  const formattedPrice = new Intl.NumberFormat('fa-IQ').format(product.price || 0);

  return (
    <div className="card card-compact bg-base-100 shadow-sm border border-base-200 hover:shadow-md hover:-translate-y-1 transition-all duration-300 h-full">
      {/* تصویر ۱۶:۹ */}
      <figure className="aspect-[16/9] bg-base-200 relative overflow-hidden">
        {product.image ? (
          <img 
            src={product.image} 
            alt={product.name} 
            loading="lazy"
            className="w-full h-full object-cover"
            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
          />
        ) : null}
        {/* فال‌بک تصویر */}
        <div className="absolute inset-0 flex items-center justify-center text-base-content/20" style={{display: product.image ? 'none' : 'flex'}}>
          <ImageOff size={24} />
        </div>
      </figure>

      <div className="card-body p-3">
        {/* عنوان محصول (محدود به ۱ خط) */}
        <h3 className="card-title text-sm font-bold text-base-content/90 line-clamp-1" title={product.name}>
          {product.name}
        </h3>
        
        {/* قیمت */}
        <div className="mt-auto flex items-baseline gap-1">
          <span className="text-lg font-black text-secondary">{formattedPrice}</span>
          <span className="text-[10px] text-base-content/60 font-medium">IQD</span>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;