// src/app/features/shop/components/OrderWizard.jsx
import { Ruler, Layers, CheckCircle, PenTool, Check, Info, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

import pageText from '../../../lang/pages.json'

const OrderWizard = ({ productData, state, setters }) => {
  const { sizes, pricing_config, quantities, options } = productData;

  // تابع کمکی برای نمایش قیمت اضافه
  const renderImpact = (val) => {
    const num = parseFloat(val);
    if (!num || num === 0) return null;
    return <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full mr-auto">+{num.toLocaleString()}</span>;
  };

  // تابع کمکی برای رندر کردن انواع فیلدهای آپشن
  const renderOptionInput = (opt) => {
    const val = state.selectedOptions[opt.id];

    switch (opt.type) {
      // ۱. منو کشویی (Dropdown)
      case 'select':
        return (
          <select
            className="select select-bordered w-full rounded-xl border-slate-200 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 text-sm"
            value={val || ''}
            onChange={(e) => setters.setSelectedOptions(p => ({ ...p, [opt.id]: e.target.value }))}
          >
            <option value="" disabled>{pageText.shop.productDetail.orderWizard.selectOption}</option>
            {opt.choices?.map(c => (
              <option key={c.id} value={c.id}>
                {c.label} {parseFloat(c.price_impact) > 0 ? `(+${parseFloat(c.price_impact).toLocaleString()} IQD)` : ''}
              </option>
            ))}
          </select>
        );

      // ۲. چند انتخابی (Checkbox blocks)
      case 'checkbox':
        const arrVal = Array.isArray(val) ? val : [];
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {opt.choices?.map(choice => {
              const isSelected = arrVal.includes(choice.id);
              return (
                <div
                  key={choice.id}
                  onClick={() => {
                    const newArr = isSelected ? arrVal.filter(id => id !== choice.id) : [...arrVal, choice.id];
                    setters.setSelectedOptions(p => ({ ...p, [opt.id]: newArr }));
                  }}
                  className={clsx(
                    "cursor-pointer p-3 rounded-xl border flex items-center gap-3 transition-all duration-200",
                    isSelected ? "border-orange-500 bg-orange-50 text-orange-900 shadow-sm" : "border-slate-200 hover:border-orange-300 bg-white"
                  )}
                >
                  <div className={clsx(
                    "w-5 h-5 rounded flex flex-shrink-0 items-center justify-center border transition-all",
                    isSelected ? "bg-orange-500 border-orange-500 text-white" : "bg-slate-100 border-slate-300"
                  )}>
                    {isSelected && <Check size={14} strokeWidth={3} />}
                  </div>
                  <span className="text-sm font-medium flex-1">{choice.label}</span>
                  {renderImpact(choice.price_impact)}
                </div>
              );
            })}
          </div>
        );

      // ۴. متن کوتاه (Short Text Input)
      case 'text':
        return (
          <input
            type="text"
            className="input input-bordered w-full rounded-xl border-slate-200 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 text-sm"
            placeholder={pageText.shop.productDetail.orderWizard.writeYourText}
            value={val || ''}
            onChange={(e) => setters.setSelectedOptions(p => ({ ...p, [opt.id]: e.target.value }))}
          />
        );

      // ۵. متن بلند (Textarea)
      case 'textarea':
        return (
          <textarea
            className="textarea textarea-bordered w-full rounded-xl border-slate-200 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20 text-sm min-h-[120px] leading-relaxed"
            placeholder={pageText.shop.productDetail.orderWizard.writeYourDescription}
            value={val || ''}
            onChange={(e) => setters.setSelectedOptions(p => ({ ...p, [opt.id]: e.target.value }))}
          />
        );

      // ۳. تک انتخابی (Radio blocks) - پیش‌فرض
      case 'radio':
      default:
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {opt.choices?.map(choice => (
              <div
                key={choice.id}
                onClick={() => setters.setSelectedOptions(p => ({ ...p, [opt.id]: choice.id }))}
                className={clsx(
                  "cursor-pointer p-3 rounded-xl border flex items-center justify-between transition-all duration-200",
                  val == choice.id
                    ? "border-orange-500 bg-orange-50 text-orange-900 shadow-sm"
                    : "border-slate-200 hover:border-orange-300 bg-white"
                )}
              >
                <div className="flex items-center gap-2">
                   <div className={clsx(
                     "w-4 h-4 rounded-full border-2 flex items-center justify-center transition-all",
                     val == choice.id ? "border-orange-500" : "border-slate-300"
                   )}>
                      {val == choice.id && <div className="w-2 h-2 bg-orange-500 rounded-full"></div>}
                   </div>
                   <span className="text-sm font-medium">{choice.label}</span>
                </div>
                {renderImpact(choice.price_impact)}
              </div>
            ))}
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col gap-8">
      
      {/* --- بخش ۱: انتخاب سایز --- */}
      <section className="bg-white rounded-[24px] border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Ruler size={22} />
          </div>
          <h3 className="font-bold text-lg text-slate-800">{pageText.shop.productDetail.orderWizard.sizes}</h3>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {sizes?.map(size => (
            <div 
              key={size.id}
              onClick={() => {
                setters.setSizeType('fixed');
                setters.setSelectedSizeId(size.id);
              }}
              className={clsx(
                "cursor-pointer rounded-2xl border-2 p-4 flex flex-col gap-1 transition-all relative overflow-hidden",
                state.sizeType === 'fixed' && state.selectedSizeId == size.id
                  ? "border-primary bg-primary/5 shadow-inner"
                  : "border-slate-100 hover:border-slate-200 bg-slate-50/50"
              )}
            >
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-700">{size.name}</span>
                {state.sizeType === 'fixed' && state.selectedSizeId == size.id && (
                  <CheckCircle size={18} className="text-primary" />
                )}
              </div>
              <div className="flex items-center justify-between text-sm text-slate-500">
                <span>{size.width} × {size.height} cm</span>
                {renderImpact(size.price_impact)}
              </div>
            </div>
          ))}

          {pricing_config?.accepts_custom_dimensions && (
            <div 
              onClick={() => setters.setSizeType('custom')}
              className={clsx(
                "cursor-pointer rounded-2xl border-2 p-4 flex flex-col justify-center gap-1 transition-all",
                state.sizeType === 'custom'
                  ? "border-primary bg-primary/5"
                  : "border-slate-100 hover:border-slate-200 border-dashed"
              )}
            >
              <span className="font-bold text-slate-700 text-center">{pageText.shop.productDetail.orderWizard.customSizes}</span>
              <span className="text-xs text-slate-400 text-center">{pageText.shop.productDetail.orderWizard.manualInput}</span>
            </div>
          )}
        </div>

        {state.sizeType === 'custom' && (
          <div className="mt-5 p-4 bg-slate-50 rounded-2xl grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2">
            <div>
              <label className="label text-xs font-bold text-slate-500">{pageText.shop.productDetail.orderWizard.height}</label>
              <input 
                type="number" 
                className="input input-bordered w-full rounded-xl"
                placeholder={ pageText.shop.productDetail.orderWizard.minWidth + pricing_config.min_width}
                value={state.customDimensions.width}
                onChange={(e) => setters.setCustomDimensions(p => ({...p, width: e.target.value}))}
              />
            </div>
            <div>
              <label className="label text-xs font-bold text-slate-500">{pageText.shop.productDetail.orderWizard.width}</label>
              <input 
                type="number" 
                className="input input-bordered w-full rounded-xl"
                placeholder={ pageText.shop.productDetail.orderWizard.maxWidth + pricing_config.max_width}
                value={state.customDimensions.height}
                onChange={(e) => setters.setCustomDimensions(p => ({...p, height: e.target.value}))}
              />
            </div>
          </div>
        )}
      </section>

      {/* --- بخش ۲: تعداد سفارش --- */}
      <section className="bg-white rounded-[24px] border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Layers size={22} />
          </div>
          <h3 className="font-bold text-lg text-slate-800">{pageText.shop.productDetail.orderWizard.quantityAndAmount}</h3>
        </div>

        {quantities?.length > 0 ? (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            {quantities.map(qty => (
              <button
                key={qty.id}
                onClick={() => setters.setSelectedQuantityId(qty.id)}
                className={clsx(
                  "py-3 px-2 rounded-xl border-2 text-center transition-all flex flex-col items-center justify-center gap-1",
                  state.selectedQuantityId == qty.id
                    ? "border-primary bg-primary text-white shadow-lg shadow-primary/30 font-bold scale-105"
                    : "border-slate-100 bg-white text-slate-600 hover:border-primary/30"
                )}
              >
                {/* 🔴 اینجا مشکل صفر شدن تیراژ با تغییر به quantity_value حل شد */}
                <div className="flex items-baseline gap-1">
                  <span>{(Number(qty.quantity_value) || 0).toLocaleString()}</span>
                  <span className="text-[10px] opacity-80">عدد</span>
                </div>
                {/* در صورت داشتن راهنما روی تیراژ */}
                {qty.guide_text && (
                  <span className="text-[9px] opacity-70 truncate w-full px-1">{qty.guide_text}</span>
                )}
              </button>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-4 bg-slate-50 p-4 rounded-2xl max-w-md">
            <button 
              className="btn btn-square btn-ghost bg-white shadow-sm border border-slate-200"
              onClick={() => setters.setCustomQuantity(Math.max(pricing_config.min_quantity || 1, state.customQuantity - 1))}
            >-</button>
            <input 
              type="number" 
              className="input input-ghost text-center text-xl font-black flex-1 bg-transparent"
              value={state.customQuantity}
              onChange={(e) => setters.setCustomQuantity(parseInt(e.target.value) || 0)}
            />
            <button 
              className="btn btn-square btn-ghost bg-white shadow-sm border border-slate-200"
              onClick={() => setters.setCustomQuantity(Math.min(pricing_config.max_quantity || 999999, state.customQuantity + 1))}
            >+</button>
          </div>
        )}
      </section>

      {/* --- بخش ۳: آپشن‌ها --- */}
      {options?.length > 0 && (
        <section className="bg-white rounded-[24px] border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center">
              <PenTool size={22} />
            </div>
            <h3 className="font-bold text-lg text-slate-800">{pageText.shop.productDetail.orderWizard.productOptions}</h3>
          </div>

          <div className="space-y-8 divide-y divide-slate-100">
            {options.map((opt, index) => (
              <div key={opt.id} className={clsx("flex flex-col gap-3", index > 0 && "pt-6")}>
                
                {/* هدر آپشن و نشانگر اجباری */}
                <div className="flex justify-between items-center">
                  <label className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                    {opt.label} 
                    {opt.is_required && <span className="text-error text-lg leading-none">*</span>}
                  </label>
                  
                  {/* تگ نشان‌دهنده انتخاب شدن برای فیلدهای غیرمتنی */}
                  {['radio', 'select', 'checkbox'].includes(opt.type) && state.selectedOptions[opt.id] && (
                     <span className="text-[10px] text-primary font-bold bg-primary/10 px-2.5 py-1 rounded-full">
                       {pageText.shop.productDetail.orderWizard.hasAnswered}
                     </span>
                  )}
                </div>

                {/* 🔴 باکس زیبای راهنما (Guide Text) */}
                {opt.guide_text && (
                  <div className={clsx(
                    "flex items-start gap-2 p-3 rounded-xl text-xs leading-relaxed",
                    opt.guide_type === 'warning' ? 'bg-amber-50 text-amber-800 border border-amber-100' : 'bg-blue-50 text-blue-800 border border-blue-100'
                  )}>
                    {opt.guide_type === 'warning' ? (
                      <AlertCircle size={16} className="mt-0.5 shrink-0 text-amber-500" />
                    ) : (
                      <Info size={16} className="mt-0.5 shrink-0 text-blue-500" />
                    )}
                    <p>{opt.guide_text}</p>
                  </div>
                )}
                
                {/* رندر شدن داینامیک اینپوت‌ها براساس نوع (Type) */}
                {renderOptionInput(opt)}
                
              </div>
            ))}
          </div>
        </section>
      )}

    </div>
  );
};

export default OrderWizard;