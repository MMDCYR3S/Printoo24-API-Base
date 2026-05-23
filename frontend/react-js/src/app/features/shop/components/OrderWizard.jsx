// src/app/features/shop/components/OrderWizard.jsx
import React, { useState } from 'react';
import { CheckCircle2 } from 'lucide-react';

// کامپوننت جداگانه برای multi_select تا state آرایه‌ای درست کار کنه
const MultiSelectField = ({ field, selectedOptions, handleOptionSelect }) => {
  const [selected, setSelected] = useState(() => {
    const val = selectedOptions[field.id];
    return Array.isArray(val) ? val.map(String) : [];
  });

  const toggle = (choiceId) => {
    const strId = String(choiceId);
    const next = selected.includes(strId)
      ? selected.filter(v => v !== strId)
      : [...selected, strId];
    setSelected(next);
    handleOptionSelect(field.id, next);
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {field.choices
        ?.sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((choice) => {
          const isSelected = selected.includes(String(choice.id));
          return (
            <button
              key={choice.id}
              type="button"
              onClick={() => toggle(choice.id)}
              className={`
                relative flex flex-col items-center justify-center text-center p-4 rounded-2xl border-2 transition-all duration-300 overflow-hidden group
                ${isSelected
                  ? "border-primary bg-primary/5 shadow-sm"
                  : "border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50"
                }
              `}
            >
              <div className={`
                absolute top-2.5 right-2.5 transition-all duration-300
                ${isSelected ? "opacity-100 scale-100" : "opacity-0 scale-50"}
              `}>
                <CheckCircle2 size={18} className="text-primary" fill="currentColor" stroke="white" />
              </div>
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
  );
};

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

  // ─── رندر محتوای هر فیلد بر اساس نوع آن ───────────────────────────────────
  const renderFieldContent = (field) => {

    // dropdown و single_select — همان منطق اصلی (مستطیل‌های زیبا)
    if (field.field_type === 'dropdown' || field.field_type === 'single_select') {
      return (
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
      );
    }

    // multi_select — کامپوننت جداگانه با local state
    if (field.field_type === 'multi_select') {
      return (
        <MultiSelectField
          field={field}
          selectedOptions={selectedOptions}
          handleOptionSelect={handleOptionSelect}
        />
      );
    }

    // text — ورودی تک‌خطی
    if (field.field_type === 'text') {
      return (
        <input
          type="text"
          value={selectedOptions[field.id] || ''}
          onChange={(e) => handleOptionSelect(field.id, e.target.value)}
          placeholder={field.description || ''}
          className="w-full px-4 py-3 rounded-2xl border-2 border-slate-100 bg-slate-50 text-sm text-slate-800 placeholder-slate-400 outline-none focus:border-primary focus:bg-white transition-all duration-300"
        />
      );
    }

    // textarea — ورودی چندخطی
    if (field.field_type === 'textarea') {
      return (
        <textarea
          value={selectedOptions[field.id] || ''}
          onChange={(e) => handleOptionSelect(field.id, e.target.value)}
          placeholder={field.description || ''}
          rows={4}
          className="w-full px-4 py-3 rounded-2xl border-2 border-slate-100 bg-slate-50 text-sm text-slate-800 placeholder-slate-400 outline-none focus:border-primary focus:bg-white transition-all duration-300 resize-none"
        />
      );
    }

    // number — ورودی عددی
    if (field.field_type === 'number') {
      return (
        <input
          type="number"
          value={selectedOptions[field.id] ?? ''}
          onChange={(e) => handleOptionSelect(field.id, e.target.value)}
          placeholder={field.description || '0'}
          className="w-full px-4 py-3 rounded-2xl border-2 border-slate-100 bg-slate-50 text-sm text-slate-800 placeholder-slate-400 outline-none focus:border-primary focus:bg-white transition-all duration-300"
        />
      );
    }

    // fallback — تایپ ناشناخته
    return null;
  };
  // ──────────────────────────────────────────────────────────────────────────

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

          {/* رندر محتوای فیلد بر اساس نوع */}
          {renderFieldContent(field)}
        </div>
      ))}
    </div>
  );
};

export default OrderWizard;