// src/app/components/layout/SearchOverlay.jsx
import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { formatCurrency } from '../utils/formatters';
import { Search, PackageOpen } from 'lucide-react';

const SearchOverlay = ({ results, loading, hasMore, onLoadMore, isVisible, onClose }) => {
  const scrollRef = useRef(null);

  if (!isVisible) return null;

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    if (scrollHeight - scrollTop <= clientHeight + 50 && !loading && hasMore) {
      onLoadMore();
    }
  };

  return (
    <div 
      className="absolute top-full left-0 right-0 mt-2 bg-white rounded-2xl shadow-2xl border border-base-200 overflow-hidden z-[60] max-h-[450px] flex flex-col"
      onMouseLeave={onClose}
    >
      <div 
        ref={scrollRef}
        onScroll={handleScroll}
        className="overflow-y-auto flex-1 p-2 space-y-1 custom-scrollbar"
      >
        {results.map((product) => (
          <Link
            key={product.id}
            to={`/product/${product.slug}`}
            // onClick={onClose}
            className="flex items-center gap-4 p-3 hover:bg-primary/5 rounded-xl transition-colors group"
          >
            <div className="w-14 h-14 rounded-lg bg-base-100 overflow-hidden border border-base-200 shrink-0">
              <img src={product.thumbnail} alt={product.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
            </div>
            <div className="flex-1 min-w-0 text-right">
              <h4 className="font-bold text-sm text-neutral truncate">{product.name}</h4>
              <p className="text-xs text-base-content/60 truncate mt-1">
                {product.category?.parent_category} / {product.category?.children_category}
              </p>
            </div>
            <div className="text-left shrink-0">
              <div className="text-primary font-black text-sm">
                {formatCurrency(product.price)} <span className="text-[10px]">IQD</span>
              </div>
            </div>
          </Link>
        ))}

        {loading && (
          <div className="p-4 flex justify-center">
            <span className="loading loading-dots loading-md text-primary"></span>
          </div>
        )}

        {!loading && results.length === 0 && (
          <div className="p-8 text-center text-base-content/40">
            <PackageOpen size={48} className="mx-auto mb-2 opacity-20" />
            <p>نتیجه‌ای یافت نشد</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchOverlay;