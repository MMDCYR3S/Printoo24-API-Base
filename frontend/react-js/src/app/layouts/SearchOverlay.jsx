// src/app/components/layout/SearchOverlay.jsx
import React, { useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { formatCurrency } from '../utils/formatters';
import { Search, PackageOpen, TrendingUp, ArrowLeft } from 'lucide-react';

const SearchOverlay = ({ results, loading, hasMore, onLoadMore, isVisible, onClose }) => {
  const overlayRef = useRef(null);
  const scrollRef = useRef(null);

  // ── بسته شدن فقط با کلیک بیرون از overlay ──
  useEffect(() => {
    if (!isVisible) return;

    const handleClickOutside = (e) => {
      if (overlayRef.current && !overlayRef.current.contains(e.target)) {
        // چک کن که کلیک روی خود اینپوت جستجو نباشه
        const searchInput = document.querySelector('[data-search-input]');
        if (searchInput && searchInput.contains(e.target)) return;
        onClose();
      }
    };

    // با تأخیر کوچک اضافه کن که کلیک فعلی trigger نشه
    const timer = setTimeout(() => {
      document.addEventListener('mousedown', handleClickOutside);
    }, 10);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible, onClose]);

  // ── اسکرول بی‌نهایت ──
  const handleScroll = useCallback(
    (e) => {
      const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
      if (scrollHeight - scrollTop <= clientHeight + 60 && !loading && hasMore) {
        onLoadMore();
      }
    },
    [loading, hasMore, onLoadMore]
  );

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          ref={overlayRef}
          initial={{ opacity: 0, y: -8, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.98 }}
          transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="
            absolute top-full left-0 right-0 mt-2 z-[60]
            bg-white/[0.98] backdrop-blur-xl
            rounded-2xl overflow-hidden
            shadow-[0_16px_50px_-10px_rgba(0,0,0,0.15)]
            ring-1 ring-black/[0.06]
            max-h-[460px] flex flex-col
          "
        >
          {/* ── هدر نتایج ── */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100/80">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center">
                <Search size={12} className="text-primary" />
              </div>
              <span className="text-xs font-bold text-slate-500">
                {loading && results.length === 0
                  ? 'Serching ...'
                  : results.length > 0
                    ? `${results.length} resault`
                    : 'resault'}
              </span>
            </div>
            {results.length > 0 && (
              <span className="text-[10px] text-slate-400 font-medium">
                
              </span>
            )}
          </div>

          {/* ── لیست نتایج ── */}
          <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="overflow-y-auto flex-1 custom-scrollbar"
          >
            <div className="p-1.5">
              {results.map((product, idx) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(idx * 0.03, 0.3), duration: 0.25 }}
                >
                  <Link
                    to={`/product/${product.slug}`}
                    onClick={onClose}
                    className="
                      flex items-center gap-3.5 p-2.5
                      rounded-xl transition-all duration-200
                      hover:bg-slate-50 group
                      active:scale-[0.99]
                    "
                  >
                    {/* تصویر */}
                    <div className="
                      w-14 h-14 rounded-xl overflow-hidden shrink-0
                      bg-gradient-to-br from-slate-50 to-slate-100
                      ring-1 ring-black/[0.05]
                      group-hover:ring-primary/20 group-hover:shadow-md group-hover:shadow-primary/5
                      transition-all duration-300
                    ">
                      <img
                        src={product.thumbnail}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                    </div>

                    {/* اطلاعات */}
                    <div className="flex-1 min-w-0 text-right">
                      <h4 className="font-bold text-[13px] text-slate-800 truncate group-hover:text-slate-900 transition-colors">
                        {product.name}
                      </h4>
                      <p className="text-[11px] text-slate-400 truncate mt-1 flex items-center gap-1">
                        <span className="inline-block w-1 h-1 rounded-full bg-slate-300" />
                        {product.category?.parent_category}
                        {product.category?.children_category && (
                          <>
                            <span className="text-slate-300">/</span>
                            {product.category.children_category}
                          </>
                        )}
                      </p>
                    </div>

                    {/* قیمت */}
                    <div className="shrink-0 text-left flex flex-col items-end gap-0.5">
                      <span className="text-primary font-extrabold text-[13px] tracking-tight dir-ltr">
                        {formatCurrency(product.price)}
                      </span>
                      <span className="text-[9px] font-bold text-slate-400 tracking-wider">
                        IQD
                      </span>
                    </div>

                    {/* فلش */}
                    <ArrowLeft
                      size={14}
                      className="
                        shrink-0 text-slate-300
                        opacity-0 -translate-x-1
                        group-hover:opacity-100 group-hover:translate-x-0
                        transition-all duration-200
                      "
                    />
                  </Link>
                </motion.div>
              ))}
            </div>

            {/* لودینگ */}
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="py-4 flex justify-center"
                >
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-1.5 h-1.5 rounded-full bg-primary/60"
                          animate={{ y: [0, -6, 0] }}
                          transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            delay: i * 0.15,
                            ease: 'easeInOut',
                          }}
                        />
                      ))}
                    </div>
                    <span className="text-xs text-slate-400 font-medium">Searching ...</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* حالت خالی */}
            {!loading && results.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="py-12 px-6 flex flex-col items-center justify-center"
              >
                <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                  <PackageOpen size={28} className="text-slate-300" />
                </div>
                <p className="text-sm font-bold text-slate-400">not found</p>
              </motion.div>
            )}
          </div>

          {/* ── فوتر ── */}
          {results.length > 0 && !loading && (
            <div className="px-4 py-2.5 border-t border-slate-100/80 bg-slate-50/50">
              <div className="flex items-center justify-center gap-1.5 text-[11px] text-slate-400">
                <kbd className="px-1.5 py-0.5 bg-white rounded text-[10px] font-mono ring-1 ring-slate-200 text-slate-500">
                  Esc
                </kbd>
                <span>close</span>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SearchOverlay;