// src/app/features/shop/components/ProductGallery.jsx
import { useState, useEffect } from 'react';
import clsx from 'clsx';
import { Image as ImageIcon } from 'lucide-react';

const ProductGallery = ({ images = [] }) => {
  const [activeImage, setActiveImage] = useState(null);

  useEffect(() => {
    if (images.length > 0) setActiveImage(images[0].image_url);
  }, [images]);

  if (!images || images.length === 0) {
    return (
      <div className="aspect-square bg-slate-50 rounded-3xl border border-slate-100 flex flex-col items-center justify-center text-slate-300">
        <ImageIcon size={48} strokeWidth={1.5} />
        <span className="mt-2 text-sm">تصویر ندارد</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 sticky top-24">
      {/* تصویر اصلی */}
      <div className="aspect-[4/3] w-full bg-white rounded-3xl border border-slate-100 p-2 shadow-sm overflow-hidden group">
        <div className="w-full h-full rounded-2xl overflow-hidden relative bg-slate-50">
           <img 
             src={activeImage} 
             alt="Product Main" 
             className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
           />
        </div>
      </div>

      {/* تصاویر کوچک */}
      <div className="grid grid-cols-4 gap-3">
        {images.map((img) => (
          <button
            key={img.id}
            onClick={() => setActiveImage(img.image_url)}
            className={clsx(
              "aspect-square rounded-2xl p-1 border-2 transition-all duration-200 bg-white",
              activeImage === img.image_url 
                ? "border-primary shadow-md scale-95" 
                : "border-transparent hover:border-slate-200"
            )}
          >
            <img 
              src={img.image_url} 
              alt="Thumb" 
              className="w-full h-full object-cover rounded-xl"
            />
          </button>
        ))}
      </div>
    </div>
  );
};

export default ProductGallery;