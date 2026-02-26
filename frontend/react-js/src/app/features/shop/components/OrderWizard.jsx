// src/app/features/shop/components/OrderWizard.jsx
import React from 'react';
import { CheckCircle2 } from 'lucide-react';

const OrderWizard = ({ productData, state, setters }) => {
  if (!productData || !Array.isArray(productData.fields)) {
    return (
      <div className="w-full h-32 flex items-center justify-center bg-slate-50 rounded-3xl border border-slate-100">
        <span className="loading loading-dots loading-md text-slate-300"></span>
      </div>
    );
  }

  const selectedOptions = state?.selectedOptions || {};
  const visibleFields = state?.visibleFields || [];
  const handleOptionSelect = setters?.handleOptionSelect || (() => {});

  const fieldsToRender = productData.fields
    .filter(field => visibleFields.includes(field.id))
    .sort((a, b) => (a.order || 0) - (b.order || 0));

  if (fieldsToRender.length === 0) return null;

  return (
    <div className="space-y-6">
      {fieldsToRender.map((field) => (
        <div 
          key={field.id} 
          className="bg-white p-5 md:p-6 rounded-3xl border border-slate-100 shadow-sm transition-all duration-300 hover:shadow-md"
        >
          {/* هدرِ فیلد */}
          <div className="flex items-center justify-between mb-4 border-b border-slate-50 pb-3">
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-4 bg-primary rounded-full"></div>
              <h3 className="text-sm md:text-base font-extrabold text-slate-800">
                {field.title}
              </h3>
              {field.is_required && <span className="text-rose-500 text-lg leading-none mt-1">*</span>}
            </div>
          </div>

          {/* گزینه‌های انتخاب (مستطیل‌های زیبا) */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {field.choices
              ?.sort((a, b) => (a.order || 0) - (b.order || 0))
              .map((choice) => {
                const isSelected = String(selectedOptions[field.id]) === String(choice.id);

                return (
                  <button
                    key={choice.id}
                    type="button"
                    onClick={() => handleOptionSelect(field.id, choice.id)}
                    className={`
                      relative flex flex-col items-center justify-center text-center p-4 rounded-2xl border-2 transition-all duration-300 overflow-hidden group
                      ${isSelected 
                        ? "border-primary bg-primary/5 shadow-sm" 
                        : "border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50"
                      }
                    `}
                  >
                    {/* آیکون تیک برای حالت فعال */}
                    <div className={`
                      absolute top-2.5 right-2.5 transition-all duration-300
                      ${isSelected ? "opacity-100 scale-100" : "opacity-0 scale-50"}
                    `}>
                      <CheckCircle2 size={18} className="text-primary" fill="currentColor" stroke="white" />
                    </div>

                    {/* عنوان گزینه */}
                    <span className={`
                      text-xs md:text-sm font-bold z-10 transition-colors mt-1
                      ${isSelected ? "text-primary" : "text-slate-600 group-hover:text-slate-900"}
                    `}>
                      {choice.title}
                    </span>
                  </button>
                );
              })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default OrderWizard;