import React from "react";
import { FormProvider } from "react-hook-form";
import { Save } from "lucide-react";
import { useStep2Form } from "../../../../hooks/useStep2Form";

import FieldsEditor from "../FieldsEditor";

const ProductStep2Fields = ({ initialData, onSave, isSaving }) => {
  // هوکی که برای استپ ۲ بازنویسی کردیم رو اینجا فراخوانی می‌کنیم
  const { methods, onSubmit } = useStep2Form(initialData, onSave);

  return (
    <FormProvider {...methods}>
      <form onSubmit={onSubmit} className="relative pb-32">
        {/* بدنه اصلی فرم‌ساز که قابلیت درگ و دراپ داره */}
        <FieldsEditor />

        {/* دکمه شناور ذخیره در پایین صفحه */}
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
          <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
            <button
              type="submit"
              disabled={isSaving}
              className="btn bg-blue-600 hover:bg-blue-700 text-white h-14 px-12 rounded-full shadow-lg shadow-blue-500/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none flex items-center"
            >
              {isSaving ? (
                <span className="loading loading-spinner"></span>
              ) : (
                <Save size={24} />
              )}
              ذخیره ساختار فرم و ادامه
            </button>
          </div>
        </div>
      </form>
    </FormProvider>
  );
};

export default ProductStep2Fields;
