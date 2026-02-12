// src/app/features/shop/ProductDetailPage.jsx
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { ShoppingCart, ShieldCheck, Truck, ChevronRight } from 'lucide-react';

import { shopService } from '../../services/shopService';
import { cartService } from '../../services/cartService';
import { useProductCalculator } from './hooks/useProductCalculator';

// ایمپورت کامپوننت‌های داخلی
import ProductGallery from './components/ProductGallery';
import OrderWizard from './components/OrderWizard';

const ProductDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  // دریافت اطلاعات محصول
  const { data, isLoading, error } = useQuery({
    queryKey: ['product-detail', slug],
    queryFn: () => shopService.getProductDetail(slug),
    retry: 1,
  });

  // محاسبات
  const { state, setters, pricing } = useProductCalculator(data);

  // افزودن به سبد
  const addToCartMutation = useMutation({
    mutationFn: cartService.addToCart,
    onSuccess: () => {
      toast.success('به سبد خرید اضافه شد');
      navigate('/cart');
    },
    onError: () => toast.error('خطا در افزودن به سبد')
  });

  const handleAddToCart = () => {
    if (!data) return;
    
    const minQty = data.pricing_config?.min_quantity || 1;
    if (data.pricing_config?.allow_custom_quantity && state.customQuantity < minQty) {
      toast.error(`حداقل سفارش ${minQty} عدد است`);
      return;
    }

    // بررسی سایز دلخواه
    if (state.sizeType === 'custom' && (!state.customDimensions.width || !state.customDimensions.height)) {
        toast.error('لطفا ابعاد طول و عرض را وارد کنید');
        return;
    }

    const payload = {
      product_id: data.product_info.id,
      selections: {
        name: data.product_info.name,
        ...(state.quantityType === 'fixed' 
           ? { quantity_id: state.selectedQuantityId } 
           : { quantity: state.customQuantity }),
        ...(state.sizeType === 'fixed'
           ? { size_id: state.selectedSizeId }
           : { custom_size: state.customDimensions }), 
        options: state.selectedOptions,
      }
    };
    addToCartMutation.mutate(payload);
  };

  if (isLoading) return <DetailSkeleton />;
  if (error || !data) return <div className="text-center py-20">محصول یافت نشد</div>;

  const { product_info } = data;

  return (
    <div className="bg-slate-50/50 min-h-screen pb-20">
      
      {/* هدر رنگی */}
      <div className="w-full h-48 bg-gradient-to-b from-primary/5 to-transparent absolute top-0 left-0 -z-10"></div>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        
        {/* نویگیشن */}
        <div className="flex items-center gap-2 text-sm text-slate-500 mb-8">
           <a href="/shop" className="hover:text-primary flex items-center gap-1">
             <ChevronRight size={16} /> محصولات
           </a>
           <span className="opacity-30">/</span>
           <span className="text-slate-800 font-bold">{product_info.name}</span>
        </div>

        {/* تغییر مهم ۱: حذف items-start 
            این باعث می‌شود ارتفاع ستون‌ها یکسان شود تا sticky بتواند در طول ستون حرکت کند 
        */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* === ستون راست: گالری === */}
          <div className="lg:col-span-4">
             {/* برای گالری هم sticky گذاشتیم که اگر فرم خیلی طولانی بود، عکس بالا نمونه */}
             <div className="sticky top-24">
                <ProductGallery images={data.images} />
             </div>
          </div>

          {/* === ستون وسط: جزئیات (طولانی‌ترین بخش) === */}
          <div className="lg:col-span-5 flex flex-col gap-8">
             
             {/* هدر محصول */}
             <div>
               <h1 className="text-3xl font-black text-slate-800 leading-snug mb-3">
                 {product_info.name}
               </h1>
               <div className="flex items-center gap-3">
                 <span className="px-3 py-1 bg-white border border-slate-200 rounded-lg text-xs font-mono text-slate-500">
                   CODE: {product_info.code}
                 </span>
                 <span className="text-sm text-primary font-bold bg-primary/5 px-3 py-1 rounded-lg">
                   {product_info.children_category}
                 </span>
               </div>
             </div>

             {/* توضیحات */}
             {product_info.description && (
               <div className="prose prose-sm max-w-none text-slate-600 bg-white p-5 rounded-2xl border border-slate-100">
                 {product_info.description}
               </div>
             )}

             {/* ویزارد سفارش */}
             <OrderWizard 
               productData={data} 
               state={state} 
               setters={setters} 
             />
          </div>

          {/* === ستون چپ: باکس قیمت شناور === */}
          <div className="lg:col-span-3 h-full"> {/* h-full مهم است */}
            
            {/* تغییر مهم ۲: استفاده از sticky و top-24 
                z-20 باعث می‌شود روی سایر المان‌ها نپرد
            */}
            <div className="sticky top-24 space-y-4 z-20">
              
              {/* کارت قیمت */}
              <div className="bg-white rounded-[24px] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden transition-all duration-300">
                <div className="p-6 bg-slate-900 text-white relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary"></div>
                  <h3 className="text-lg font-bold">فاکتور سفارش</h3>
                  <div className="mt-4 flex flex-col gap-1">
                    <span className="text-xs opacity-70">مبلغ نهایی برای {pricing.finalQuantity.toLocaleString()} عدد</span>
                    <div className="flex items-baseline gap-2">
                       <span className="text-3xl font-black tracking-tight">{pricing.totalPrice.toLocaleString()}</span>
                       <span className="text-sm font-bold text-primary">IQD</span>
                    </div>
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  <div className="space-y-2 text-sm text-slate-600">
                    <div className="flex justify-between">
                      <span>قیمت واحد پایه:</span>
                      <span className="font-medium">{pricing.baseUnitPrice.toLocaleString()}</span>
                    </div>
                    {pricing.extraCosts > 0 && (
                      <div className="flex justify-between text-emerald-600">
                        <span>آپشن‌ها و سایز:</span>
                        <span className="font-medium">+{pricing.extraCosts.toLocaleString()}</span>
                      </div>
                    )}
                  </div>

                  <div className="divider my-2"></div>

                  <button 
                    onClick={handleAddToCart}
                    disabled={addToCartMutation.isLoading}
                    className="btn btn-primary w-full h-12 rounded-xl text-lg shadow-lg shadow-primary/25"
                  >
                    {addToCartMutation.isLoading ? (
                      <span className="loading loading-dots"></span>
                    ) : (
                      <>
                        <ShoppingCart size={20} />
                        افزودن به سبد خرید
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* باکس اطمینان */}
              <div className="bg-white rounded-2xl p-5 border border-slate-100 text-xs text-slate-500 space-y-3 shadow-sm">
                <div className="flex items-center gap-3">
                  <ShieldCheck className="text-emerald-500" size={18} />
                  <span>تضمین سلامت فیزیکی کالا</span>
                </div>
                <div className="flex items-center gap-3">
                  <Truck className="text-blue-500" size={18} />
                  <span>ارسال ایمن به سراسر کشور</span>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

const DetailSkeleton = () => (
  <div className="container mx-auto px-4 py-12 grid grid-cols-1 lg:grid-cols-12 gap-8">
     <div className="lg:col-span-4 h-96 bg-gray-200 rounded-3xl animate-pulse"></div>
     <div className="lg:col-span-5 space-y-6">
       <div className="h-10 w-3/4 bg-gray-200 rounded-xl animate-pulse"></div>
       <div className="h-40 w-full bg-gray-200 rounded-xl animate-pulse"></div>
       <div className="h-64 w-full bg-gray-200 rounded-xl animate-pulse"></div>
     </div>
     <div className="lg:col-span-3 h-80 bg-gray-200 rounded-3xl animate-pulse"></div>
  </div>
);

export default ProductDetailPage;