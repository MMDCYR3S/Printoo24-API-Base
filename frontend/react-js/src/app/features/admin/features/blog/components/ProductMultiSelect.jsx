import React, { useState, useRef, useEffect } from 'react';
import { Search, ChevronDown, X, Check } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

const ProductMultiSelect = ({ options = [], value = [], onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) setIsOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredOptions = options.filter(opt => 
    opt.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    opt.code?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleToggle = (id) => {
    onChange(value.includes(id) ? value.filter(v => v !== id) : [...value, id]);
  };

  const handleRemove = (e, id) => {
    e.stopPropagation();
    onChange(value.filter(v => v !== id));
  };

  const selectedOptions = options.filter(opt => value.includes(opt.id));

  return (
    <div className="relative w-full" ref={wrapperRef}>
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          "min-h-[3rem] w-full bg-slate-50 border rounded-xl p-2 cursor-pointer flex items-center justify-between transition-all",
          isOpen ? "border-primary ring-2 ring-primary/20" : "border-slate-200 hover:border-slate-300"
        )}
      >
        <div className="flex flex-wrap gap-2 items-center w-full pr-2">
          {selectedOptions.length === 0 && <span className="text-slate-400 text-sm">جستجو و انتخاب محصولات...</span>}
          {selectedOptions.map(opt => (
            <span key={opt.id} className="badge bg-primary text-white border-0 gap-1 pl-1 py-3 text-xs shadow-sm">
              {opt.name}
              <button type="button" onClick={(e) => handleRemove(e, opt.id)} className="hover:bg-blue-700 rounded-full p-0.5 transition-colors">
                <X size={12} strokeWidth={3} />
              </button>
            </span>
          ))}
        </div>
        <ChevronDown size={18} className={clsx("text-slate-400 transition-transform flex-shrink-0 ml-2", isOpen && "rotate-180")} />
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-slate-100 rounded-2xl shadow-2xl shadow-slate-200/50 overflow-hidden"
          >
            <div className="p-3 border-b border-slate-100 relative">
              <Search size={16} className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-400" />
              <input 
                type="text" placeholder="جستجوی نام یا کد محصول..." value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input input-sm w-full bg-slate-50 border-slate-200 rounded-lg pr-10 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                onClick={e => e.stopPropagation()}
              />
            </div>
            
            <div className="max-h-60 overflow-y-auto p-2 space-y-1">
              {filteredOptions.length === 0 ? (
                <div className="p-4 text-center text-sm text-slate-400">محصولی یافت نشد.</div>
              ) : (
                filteredOptions.map(opt => {
                  const isSelected = value.includes(opt.id);
                  return (
                    <div 
                      key={opt.id} onClick={() => handleToggle(opt.id)}
                      className={clsx(
                        "flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition-colors text-sm",
                        isSelected ? "bg-primary/5 font-bold text-primary" : "hover:bg-slate-50 text-slate-700"
                      )}
                    >
                      <div className={clsx(
                        "w-5 h-5 rounded-md border flex items-center justify-center transition-all",
                        isSelected ? "bg-primary border-primary text-white scale-110" : "border-slate-300 bg-white"
                      )}>
                        {isSelected && <Check size={14} strokeWidth={3} />}
                      </div>
                      <div className="flex-1 truncate">{opt.name}</div>
                      {opt.code && <div className="text-[10px] font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md dir-ltr">{opt.code}</div>}
                    </div>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ProductMultiSelect;