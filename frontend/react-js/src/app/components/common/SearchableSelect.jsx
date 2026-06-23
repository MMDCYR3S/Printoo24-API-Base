import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Search, ChevronDown } from 'lucide-react';

const SearchableSelect = ({
  options = [],
  value,
  onChange,
  placeholder = 'هەڵبژێرە...',
  isLoading = false,
  renderOption,     // تابعی برای شخصی‌سازی ظاهر هر آیتم در لیست
  getDisplayValue,  // تابعی برای استخراج متنی که بعد از انتخاب باید در باکس اصلی نشان داده شود
  filterBy,         // تابعی برای منطق جستجو
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef(null);

  // بستن لیست با کلیک خارج از کادر (Click Outside)
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // فیلتر کردن آپشن‌ها بر اساس متن جستجو
  const filteredOptions = useMemo(() => {
    if (!searchTerm) return options;
    return options.filter(opt => filterBy(opt, searchTerm.toLowerCase()));
  }, [options, searchTerm, filterBy]);

  const handleSelect = (option) => {
    onChange(option); // ارسال کل آبجکت به والد
    setSearchTerm('');
    setIsOpen(false);
  };

  // مقداری که پس از انتخاب باید در باکس نمایش داده شود
  const displayValue = value ? getDisplayValue(value) : '';

  return (
    <div className="relative w-full" ref={wrapperRef}>
      {/* باکس اصلی (Trigger) */}
      <div
        className={`flex items-center justify-between w-full px-4 py-3 bg-white border rounded-xl cursor-pointer transition-colors ${
          isOpen ? 'border-primary ring-1 ring-primary' : 'border-slate-300 hover:border-slate-400'
        }`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex-1 truncate text-sm">
          {isLoading ? (
            <span className="text-slate-500 flex items-center gap-2">
              <span className="loading loading-spinner loading-xs"></span> لە وەرگرتندایە...
            </span>
          ) : displayValue ? (
            <span className="font-medium text-slate-700">{displayValue}</span>
          ) : (
            <span className="text-slate-400">{placeholder}</span>
          )}
        </div>
        <ChevronDown size={18} className={`text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180 text-primary' : ''}`} />
      </div>

      {/* منوی بازشونده (Dropdown) */}
      {isOpen && !isLoading && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl animate-in fade-in slide-in-from-top-2">
          
          {/* باکس جستجو */}
          <div className="p-2 border-b border-slate-100 sticky top-0 bg-white rounded-t-xl z-10">
            <div className="relative">
              <Search size={16} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                className="w-full pl-3 pr-10 py-2.5 text-sm bg-slate-50 border-none rounded-lg focus:ring-1 focus:ring-primary/30 outline-none transition-all"
                placeholder="بۆی بگەڕە..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onClick={(e) => e.stopPropagation()} // جلوگیری از بسته شدن لیست موقع کلیک روی اینپوت سرچ
                autoFocus
              />
            </div>
          </div>

          {/* لیست نتایج */}
          <div className="max-h-60 overflow-y-auto p-1 text-slate-700">
            {filteredOptions.length === 0 ? (
              <div className="p-4 text-center text-sm text-slate-400 border-2 border-dashed border-slate-100 rounded-lg m-1">
                هیچ ئەنجامێک نەدۆزرایەوە
              </div>
            ) : (
              filteredOptions.map((option, idx) => {
                const isSelected = value?.id === option.id;
                return (
                  <div
                    key={option.id || idx}
                    onClick={() => handleSelect(option)}
                    className={`p-3 mb-1 cursor-pointer rounded-lg transition-colors ${
                      isSelected ? 'bg-primary/10 border-r-4 border-primary' : 'hover:bg-slate-50 border-r-4 border-transparent'
                    }`}
                  >
                    {/* اگر رندر اختصاصی پاس داده شده بود از آن استفاده کن، وگرنه همان متن ساده را نشان بده */}
                    {renderOption ? renderOption(option, isSelected) : getDisplayValue(option)}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchableSelect;