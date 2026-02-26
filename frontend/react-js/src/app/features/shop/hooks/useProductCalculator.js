// src/app/features/shop/components/OrderWizard.jsx
import React from 'react';

// مقداردهی اولیه دیفالت (={}) برای پراپ‌ها که اگر undefined فرستاده شد، کرش نکند
const OrderWizard = ({ productData = {}, state = {}, setters = {} }) => {
  // محافظت قوی هنگام اکسترکت کردن
  const { selectedOptions = {}, visibleFields = [] } = state;
  const { handleOptionSelect = () => {} } = setters;

  if (!productData?.fields || productData.fields.length === 0) {
    return null; // اگر فیلدی از سرور نیامده بود، فرم رو رندر نکن
  }

  return (
    <div className="bg-white p-5 md:p-6 rounded-3xl border border-slate-100 shadow-sm space-y-5">
      <h3 className="text-base font-extrabold text-slate-800 mb-2 border-b border-slate-100 pb-3">
        مشخصات سفارش
      </h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {productData.fields
          .filter(field => visibleFields.includes(field.id)) // اعمال شروط
          .sort((a, b) => a.order - b.order)
          .map(field => (
            <div key={field.id} className="form-control w-full">
              <label className="label py-1.5 flex items-center gap-1">
                <span className="text-sm font-bold text-slate-700">
                  {field.title}
                </span>
                {field.is_required && <span className="text-red-500 text-lg leading-none">*</span>}
              </label>
              
              <select
                className="select select-bordered w-full bg-slate-50/50 border-slate-200 focus:border-primary focus:bg-white transition-colors"
                value={selectedOptions[field.id] || ''}
                onChange={(e) => handleOptionSelect(field.id, parseInt(e.target.value))}
              >
                {!field.is_required && (
                  <option value="">انتخاب کنید...</option>
                )}
                
                {field.choices
                  ?.sort((a, b) => a.order - b.order)
                  .map(choice => (
                    <option key={choice.id} value={choice.id}>
                      {choice.title}
                    </option>
                  ))}
              </select>
            </div>
        ))}
      </div>
    </div>
  );
};

export default OrderWizard;