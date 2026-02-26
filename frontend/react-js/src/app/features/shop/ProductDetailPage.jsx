// src/app/features/shop/ProductDetailPage.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { ShoppingCart, ShieldCheck, Truck, ChevronRight, AlertCircle } from 'lucide-react';

import { shopService } from '../../services/shopService';
import { cartService } from '../../services/cartService';
import { useProductCalculator } from './hooks/useProductCalculator';

import ProductGallery from './components/ProductGallery';
import OrderWizard from './components/OrderWizard';
import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const ProductDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['product-detail', slug],
    queryFn: () => shopService.getProductDetail(slug),
    retry: 1,
  });

  const { 
    state = { selectedOptions: {}, visibleFields: [] }, 
    setters = {}, 
    pricing = { totalPrice: 0, isCalculating: false, error: null }, 
    getSubmitPayload = () => ({})
  } = useProductCalculator(data) || {};

  const addToCartMutation = useMutation({
    mutationFn: cartService.addToCart,
    onSuccess: (response) => {
      toast.success(pageText.shop.productDetail.addToCartSuccess || "با موفقیت به سبد خرید اضافه شد.");
      const itemId = response?.id || response?.item_id;
      if (itemId) navigate(`/cart/upload/${itemId}`);
      else navigate('/cart');
    },
    onError: (err) => {
      console.error("Cart Error:", err.response?.data);
      toast.error(err.response?.data?.error || "خطا در افزودن به سبد خرید");
    }
  });

  const handleAddToCart = () => {
    const payloadInfo = getSubmitPayload();
    
    // ولیدیشن فیلدهای اجباری
    const requiredFields = (data?.fields || []).filter(f => f.is_required && state.visibleFields.includes(f.id));
    for (let f of requiredFields) {
      if (!state.selectedOptions[f.id]) {
        toast.error(`لطفاً فیلد "${f.title}" را انتخاب کنید.`);
        return;
      }
    }

    const payload = {
      product_id: payloadInfo.product_id,
      selections: {
        has_design: true,
        options: payloadInfo.options 
      }
    };

    addToCartMutation.mutate(payload);
  };

  if (isLoading) return <DetailSkeleton />;
  if (error || !data) return <div className="text-center py-20 font-bold text-slate-500">محصول یافت نشد</div>;

  return (
    <div className="bg-slate-50/50 min-h-screen pb-20">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-slate-500 mb-8">
           <a href="/shop" className="hover:text-primary flex items-center gap-1 transition-colors">
             <ChevronRight size={16} /> فروشگاه
           </a>
           <span className="opacity-30">/</span>
           <span className="text-slate-800 font-bold truncate">{data?.name}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 xl:gap-8">
          
          {/* گالری تصویر (ستون راست در دسکتاپ) */}
          <div className="lg:col-span-4">
             <div className="sticky top-24">
               <ProductGallery images={data?.images || []} attachments={data?.attachments || []} />
             </div>
          </div>

          {/* محتوای اصلی و ویزارد (ستون وسط) */}
          <div className="lg:col-span-5 flex flex-col gap-6">
             {/* هدر محصول */}
             <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
               <h1 className="text-2xl md:text-3xl font-black text-slate-800 leading-snug mb-3">
                 {data?.name}
               </h1>
               <div className="flex items-center gap-3">
                 <span className="px-3 py-1 bg-slate-100 rounded-lg text-xs font-mono text-slate-500 font-bold">
                   کد: {data?.code}
                 </span>
               </div>
               {data?.description && (
                 <div className="mt-5 pt-5 border-t border-slate-100 prose prose-sm max-w-none text-slate-600 leading-relaxed">
                   {data.description}
                 </div>
               )}
             </div>

             {/* فرمول ویزارد - تعاملی */}
             {data && state && setters && (
               <OrderWizard productData={data} state={state} setters={setters} />
             )}
          </div>

          {/* سایدبار اطلاعات مالی (ستون چپ) */}
          <div className="lg:col-span-3 h-full"> 
            <div className="sticky top-24 space-y-4">
              
              <div className="bg-white rounded-[24px] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                <div className="p-6 bg-slate-900 text-white relative">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary"></div>
                  <h3 className="text-lg font-bold">پیش‌فاکتور سفارش</h3>
                  
                  <div className="mt-6 flex flex-col gap-1 min-h-[60px] justify-center">
                    {pricing?.isCalculating ? (
                      <div className="flex items-center gap-3 text-emerald-400">
                        <span className="loading loading-dots loading-md"></span>
                        <span className="text-sm font-medium opacity-80 animate-pulse">در حال استعلام...</span>
                      </div>
                    ) : (
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl md:text-4xl font-black tracking-tight text-emerald-400">
                          {Number(pricing?.totalPrice || 0).toLocaleString()}
                        </span>
                        <span className="text-sm font-bold opacity-80">{globalText.currency || 'تومان'}</span>
                      </div>
                    )}
                  </div>

                  {/* ارور سرور در سایدبار */}
                  {pricing?.error && !pricing?.isCalculating && (
                     <div className="flex items-start gap-2 text-rose-300 text-xs font-bold mt-4 bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
                        <AlertCircle size={16} className="shrink-0 mt-0.5" />
                        <span className="leading-relaxed">{pricing.error}</span>
                     </div>
                  )}
                </div>

                <div className="p-5 bg-white space-y-4">
                  <button 
                    onClick={handleAddToCart}
                    disabled={addToCartMutation.isLoading || !data?.has_price || pricing?.isCalculating || pricing?.error}
                    className="btn btn-primary w-full h-14 rounded-xl text-base font-bold shadow-lg shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed group"
                  >
                    {addToCartMutation.isLoading ? (
                      <span className="loading loading-dots"></span>
                    ) : (
                      <>
                        <ShoppingCart size={20} className="group-hover:scale-110 transition-transform" />
                        {data?.has_price ? "افزودن به سبد خرید" : "استعلام قیمت"}
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* آیکون‌های اعتماد */}
              <div className="bg-white rounded-2xl p-5 border border-slate-100 text-xs font-bold text-slate-500 space-y-4 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-50 rounded-lg text-emerald-500">
                    <ShieldCheck size={20} />
                  </div>
                  <span>تضمین سلامت فیزیکی محصول</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-50 rounded-lg text-blue-500">
                    <Truck size={20} />
                  </div>
                  <span>ارسال سریع و مطمئن</span>
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
     <div className="lg:col-span-4 h-[400px] bg-slate-200 rounded-3xl animate-pulse"></div>
     <div className="lg:col-span-5 space-y-6">
       <div className="h-40 bg-slate-200 rounded-3xl animate-pulse"></div>
       <div className="h-60 bg-slate-200 rounded-3xl animate-pulse"></div>
     </div>
     <div className="lg:col-span-3 h-80 bg-slate-200 rounded-3xl animate-pulse"></div>
  </div>
);

export default ProductDetailPage;