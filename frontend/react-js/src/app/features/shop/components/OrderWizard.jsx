// src/app/features/shop/components/OrderWizard.jsx
import { Ruler, Layers, CheckCircle, PenTool } from 'lucide-react';
import clsx from 'clsx';

const OrderWizard = ({ productData, state, setters }) => {
  const { sizes, pricing_config, quantities, options } = productData;

  // تابع کمکی برای نمایش قیمت اضافه
  const renderImpact = (val) => {
    const num = parseFloat(val);
    if (!num || num === 0) return null;
    return <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full mr-auto">+{num.toLocaleString()}</span>;
  };

  return (
    <div className="flex flex-col gap-8">
      
      {/* --- بخش ۱: انتخاب سایز --- */}
      <section className="bg-white rounded-[24px] border border-slate-100 p-6 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Ruler size={22} />
          </div>
          <h3 className="font-bold text-lg text-slate-800">ابعاد و سایز</h3>
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

          {/* گزینه سایز دلخواه */}
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
              <span className="font-bold text-slate-700 text-center">ابعاد سفارشی</span>
              <span className="text-xs text-slate-400 text-center">وارد کردن دستی</span>
            </div>
          )}
        </div>

        {/* ورودی‌های سایز دلخواه */}
        {state.sizeType === 'custom' && (
          <div className="mt-5 p-4 bg-slate-50 rounded-2xl grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2">
            <div>
              <label className="label text-xs font-bold text-slate-500">طول (mm)</label>
              <input 
                type="number" 
                className="input input-bordered w-full rounded-xl"
                placeholder={`حداقل ${pricing_config.min_width}`}
                value={state.customDimensions.width}
                onChange={(e) => setters.setCustomDimensions(p => ({...p, width: e.target.value}))}
              />
            </div>
            <div>
              <label className="label text-xs font-bold text-slate-500">عرض (mm)</label>
              <input 
                type="number" 
                className="input input-bordered w-full rounded-xl"
                placeholder={`حداکثر ${pricing_config.max_width}`}
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
          <h3 className="font-bold text-lg text-slate-800">تیراژ و تعداد</h3>
        </div>

        {quantities?.length > 0 ? (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            {quantities.map(qty => (
              <button
                key={qty.id}
                onClick={() => setters.setSelectedQuantityId(qty.id)}
                className={clsx(
                  "py-3 px-2 rounded-xl border-2 text-center transition-all",
                  state.selectedQuantityId == qty.id
                    ? "border-primary bg-primary text-white shadow-lg shadow-primary/30 font-bold scale-105"
                    : "border-slate-100 bg-white text-slate-600 hover:border-primary/30"
                )}
              >
                {parseInt(qty.quantity).toLocaleString()} <span className="text-[10px] opacity-80">عدد</span>
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
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center">
              <PenTool size={22} />
            </div>
            <h3 className="font-bold text-lg text-slate-800">ویژگی‌های محصول</h3>
          </div>

          <div className="space-y-6">
            {options.map((opt) => (
              <div key={opt.id} className="flex flex-col gap-3">
                <div className="flex justify-between items-center">
                  <label className="text-sm font-bold text-slate-700">
                    {opt.label} {opt.is_required && <span className="text-error">*</span>}
                  </label>
                  {state.selectedOptions[opt.id] && (
                     <span className="text-xs text-primary font-medium bg-primary/5 px-2 py-1 rounded-lg">انتخاب شده</span>
                  )}
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {opt.choices?.map(choice => (
                    <div
                      key={choice.id}
                      onClick={() => setters.setSelectedOptions(prev => ({ ...prev, [opt.id]: choice.id }))}
                      className={clsx(
                        "cursor-pointer p-3 rounded-xl border flex items-center justify-between transition-all",
                        state.selectedOptions[opt.id] == choice.id
                          ? "border-orange-500 bg-orange-50 text-orange-900"
                          : "border-slate-200 hover:border-orange-300"
                      )}
                    >
                      <span className="text-sm font-medium">{choice.label}</span>
                      {renderImpact(choice.price_impact)}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

    </div>
  );
};

export default OrderWizard;