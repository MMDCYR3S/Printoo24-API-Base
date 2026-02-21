import React from 'react';
import { FormProvider } from 'react-hook-form';
import { Save } from 'lucide-react';
import { useStep2Form, Step2Context } from '../../../../hooks/useStep2Form';

import OptionsEditor from './OptionsEditor'; 
import LivePreview from './LivePreview';

// پراپ productId اضافه شد
const ProductStep2Options = ({ productId, initialData, onSave, isSaving }) => {
    
    // پاس دادن productId به هوک برای فچ کردن تیراژها
    const { methods, onSubmit, step2ContextValue } = useStep2Form(productId, initialData, onSave);

    return (
        <Step2Context.Provider value={step2ContextValue}>
            <FormProvider {...methods}>
                <form onSubmit={onSubmit} className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-32 relative">
                    {/* ساختار کدهای این بخش هیچ تغییری نکرده... */}
                    <div className="xl:col-span-7 flex flex-col gap-6">
                        <OptionsEditor />
                    </div>

                    <div className="xl:col-span-5 relative">
                        <div className="sticky top-32 pt-2">
                            <LivePreview />
                        </div>
                    </div>

                    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
                        <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
                            <button type="submit" disabled={isSaving} className="btn btn-primary h-14 px-12 rounded-full shadow-lg shadow-primary/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none flex items-center">
                                {isSaving ? <span className="loading loading-spinner"></span> : <Save size={24}/>}
                                ذخیره و نهایی‌سازی ویژگی‌ها
                            </button>
                        </div>
                    </div>
                </form>
            </FormProvider>
        </Step2Context.Provider>
    );
};

export default ProductStep2Options;