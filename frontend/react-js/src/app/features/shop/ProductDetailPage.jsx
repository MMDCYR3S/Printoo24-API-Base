// src/app/features/shop/ProductDetailPage.jsx
import { useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import {
  ShoppingCart,
  ChevronRight,
  AlertCircle,
  PhoneCall,
  ShieldAlert,
} from 'lucide-react';

import { shopService } from '../../services/shopService';
import { cartService } from '../../services/cartService';
import { useProductCalculator } from './hooks/useProductCalculator';

// ← هوک fix قطعی sticky با JavaScript
import { useStickyFix } from './hooks/useStickyFix';

import ProductGallery from './components/ProductGallery';
import OrderWizard from './components/OrderWizard';
import AdminOrderPanel from './components/AdminOrderPanel';
import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';
import SEO from '../../components/common/SEO'

/**
 * تشخیص کاربر ادمین از localStorage
 */
const checkIsAdmin = () => {
  try {
    const raw = localStorage.getItem('userData');
    if (!raw) return false;
    const data = JSON.parse(raw);
    return data?.is_superuser === true;
  } catch {
    return false;
  }
};

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
    getSubmitPayload = () => ({}),
  } = useProductCalculator(data) || {};

  const isAdmin = checkIsAdmin();

  // ← ref روی sticky element سایدبار (هدف fix)
  const sidebarStickyRef = useRef(null);
  // ← فعال‌سازی fix در این صفحه (با unmount، ancestorها restore می‌شوند)
  useStickyFix({ targetRef: sidebarStickyRef, debug: false });

  const addToCartMutation = useMutation({
    mutationFn: cartService.addToCart,
    onSuccess: (response) => {
      toast.success(
        pageText.shop.productDetail.addToCartSuccess ||
          'بە سەرکەوتوویی زیادکرا بۆ سەبەتی کڕین'
      );
      const itemId = response?.id || response?.item_id;
      if (itemId) navigate(`/cart/upload/${itemId}`);
      else navigate('/cart');
    },
    onError: (err) => {
      console.error('Cart Error:', err.response?.data);
      toast.error(
        err.response?.data?.error || ' هەڵە لە زیادکردن بۆ سەبەتی کڕین'
      );
    },
  });

  const handleAddToCart = () => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      navigate('/login');
      return;
    }

    const payloadInfo = getSubmitPayload();

    const requiredFields = (data?.fields || []).filter(
      (f) => f.is_required && state.visibleFields.includes(f.id)
    );
    for (let f of requiredFields) {
      if (!state.selectedOptions[f.id]) {
        toast.error(`تکایە"${f.title}"هەڵبژێرە`);
        return;
      }
    }

    const payload = {
      product_id: payloadInfo.product_id,
      selections: { ...payloadInfo.options },
    };

    addToCartMutation.mutate(payload);
  };

  const isAddToCartDisabled =
    addToCartMutation.isLoading ||
    !data?.has_price ||
    pricing?.isCalculating ||
    !!pricing?.error;



if (isLoading) return <DetailSkeleton />;
if (error || !data) return <div className="text-center py-20 font-bold text-slate-500">بەرهەم نەدۆزرایەوە</div>;

  return (
  
    <div>
      
    <SEO 
      title={data.name}
      description={data.description}
      keywords={data.name}
    />


      {/* ── صفحه اصلی ──
          ⚠️ min-h-screen حذف شد! طبق تحقیق Philip Walton:
          "flex items ignore their parent container's height if it's set
          via the min-height property" — min-h-screen داخل flex-1 parent
          باعث circular sizing می‌شود و sticky را می‌شکند. */}
      <div className="bg-slate-50/50 pb-20">
      
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-8">
            <a
              href="/shop"
              className="hover:text-primary flex items-center gap-1 transition-colors"
            >
              <ChevronRight size={16} /> فرۆشگاە
            </a>
            <span className="opacity-30">/</span>
            <span className="text-slate-800 font-bold truncate">
              {data?.name}
            </span>
          </div>

          {/* ← نشان ادمین */}
          {isAdmin && (
            <div className="mb-6 flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-700 text-xs font-bold px-4 py-2.5 rounded-xl">
              <ShieldAlert size={15} />
              شما در حالت ادمین هستید — می‌توانید سفارش را به‌نام مشتری ثبت کنید.
            </div>
          )}

          {/* Grid
              ⚠️ items-start حذف شد! طبق تحقیق:
              items-start باعث می‌شود هر ستون ارتفاع مستقل داشته باشد و
              sticky فضای کافی برای حرکت نداشته باشد. با default (stretch)
              ارتفاع ستون با بلندترین ستون برابر می‌شود. */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 xl:gap-8">
            {/* گالری تصویر */}
            <div className="lg:col-span-4">
              <div className="sticky top-24">
                <ProductGallery
                  images={data?.images || []}
                  attachments={data?.attachments || []}
                />
              </div>
            </div>

            {/* محتوای اصلی و ویزارد */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                <h1 className="text-2xl md:text-3xl font-black text-slate-800 leading-snug mb-3">
                  {data?.name}
                </h1>
                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 bg-slate-100 rounded-lg text-xs font-mono text-slate-500 font-bold">
                    {data?.code}
                  </span>
                </div>
                {data?.description && (
                  <div className="mt-5 pt-5 border-t border-slate-100 prose prose-sm max-w-none text-slate-600 leading-relaxed">
                    {data.description}
                  </div>
                )}
              </div>

              {data && state && setters && (
                <OrderWizard
                  productData={data}
                  state={state}
                  setters={setters}
                />
              )}

              {/* ← پنل ادمین (موبایل) */}
              {isAdmin && (
                <div className="lg:hidden">
                  <AdminOrderPanel
                    productData={data}
                    getSubmitPayload={getSubmitPayload}
                    pricing={pricing}
                    hasPrice={data?.has_price}
                  />
                </div>
              )}
            </div>

            {/* ── سایدبار دسکتاپ ── */}
            <div className="hidden lg:block lg:col-span-3">
              {/* sticky container
                  - top-24: چسبیدن به 6rem از بالای viewport (زیر هدر)
                  - z-20: لایه‌بندی روی سایر المان‌ها
                  - ref برای useStickyFix که ancestors را fix می‌کند */}
              <div
                ref={sidebarStickyRef}
                className="sticky top-24 space-y-4 z-20"
              >
                {/* باکس قیمت */}
                <div className="bg-white rounded-[24px] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                  <div className="p-6 bg-slate-900 text-white relative">
                    <h3 className="text-lg font-bold">نرخ</h3>

                    <div className="mt-6 flex flex-col gap-1 min-h-[60px] justify-center">
                      {pricing?.isCalculating ? (
                        <div className="flex items-center gap-3 text-emerald-400">
                          <span className="loading loading-dots loading-md"></span>
                          <span className="text-sm font-medium opacity-80 animate-pulse">
                            {' '}
                            لە چاوەڕوانی نرخدا...{' '}
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl md:text-4xl font-black tracking-tight text-emerald-400">
                            {Number(pricing?.totalPrice || 0).toLocaleString()}
                          </span>
                          <span className="text-sm font-bold opacity-80">
                            {globalText.currency || 'IQD'}
                          </span>
                        </div>
                      )}
                    </div>

                    {pricing?.error && !pricing?.isCalculating && (
                      <div className="flex items-start gap-2 text-rose-300 text-xs font-bold mt-4 bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
                        <AlertCircle
                          size={16}
                          className="shrink-0 mt-0.5"
                        />
                        <span className="leading-relaxed">
                          {pricing.error}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="p-5 bg-white space-y-4">
                    {data?.has_price ? (
                      <button
                        onClick={handleAddToCart}
                        disabled={isAddToCartDisabled}
                        className="btn btn-primary w-full h-14 rounded-xl text-base font-bold shadow-lg shadow-primary/25 disabled:opacity-50 disabled:cursor-not-allowed group"
                      >
                        {addToCartMutation.isLoading ? (
                          <span className="loading loading-dots"></span>
                        ) : (
                          <>
                            <ShoppingCart
                              size={20}
                              className="group-hover:scale-110 transition-transform"
                            />
                            زیاد کردن به سەبەتەی کڕین
                          </>
                        )}
                      </button>
                    ) : (
                      <a
                        href="https://wa.me/9647762278666"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full flex items-center justify-center gap-2 bg-amber-50 text-amber-600 hover:bg-amber-100 rounded-xl py-3.5 border border-amber-100 font-bold transition-all h-14"
                      >
                        <PhoneCall size={20} />
                        داوا کردنی نرخ
                      </a>
                    )}
                  </div>
                </div>

                {/* ← پنل ادمین (دسکتاپ) — زیر باکس قیمت */}
                {isAdmin && (
                  <AdminOrderPanel
                    productData={data}
                    getSubmitPayload={getSubmitPayload}
                    pricing={pricing}
                    hasPrice={data?.has_price}
                  />
                )}
              </div>
            </div>
            {/* ── /سایدبار دسکتاپ ── */}
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════
          Sticky Bottom Bar — فقط موبایل
      ══════════════════════════════════════════ */}
      <div className="flex items-center justify-center ">
        <div className="lg:hidden fixed bottom-2 w-[97vw] pb-2  z-50  ">
          <div className="absolute inset-0 bg-white/20 backdrop-blur-sm  rounded-2xl" />

          <div className="relative px-1 pt-2 flex flex-row justify-between items-center gap-1">
            <div className="h-[56px] w-full bg-slate-900 rounded-2xl px-2 py-1.5 sm:py-2.5 flex flex-col justify-center text-center">
              {/* <p className="text-[12px] text-slate-400 font-bold mb-0.5 leading-none">
                نرخ
              </p> */}

              {pricing?.isCalculating ? (
                <div className="flex items-center gap-2  text-emerald-400 mt-1 text-center">
                  <span className="loading loading-dots loading-xs"></span>
                  <span className="text-xs font-medium opacity-80">
                    لە حیسابکردندایە...
                  </span>
                </div>
              ) : pricing?.error ? (
                <div className="flex items-center gap-1.5 text-rose-400">
                  <AlertCircle size={13} className="shrink-0" />
                  <span className="text-xs font-bold truncate">
                    {pricing.error}
                  </span>
                </div>
              ) : (
                <div className="flex mx-auto items-center gap-1 mt-2">
                  <span className="text-xs text-slate-400">
                    {globalText.currency || 'IQD'}
                  </span>
                  <span className="text-xl font-black tracking-tight text-emerald-400 leading-none">
                    {Number(pricing?.totalPrice || 0).toLocaleString()}
                  </span>
                </div>
              )}
            </div>

            <button
              onClick={handleAddToCart}
              disabled={isAddToCartDisabled}
              className="btn btn-primary h-[56px] px-2 rounded-2xl text-sm font-bold shadow-lg shadow-primary/30 disabled:opacity-50 disabled:cursor-not-allowed shrink-0 flex items-center gap-2 transition-all active:scale-95"
            >
              {addToCartMutation.isLoading ? (
                <span className="loading loading-dots loading-sm"></span>
              ) : (
                <>
                  <ShoppingCart size={18} />
                  <span>
                    {data?.has_price
                      ? 'زیاد کردن به سەبەتەی کڕین'
                      : 'داوا کردنی نرخ'}
                  </span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
      {/* ══ /Sticky Bottom Bar ══ */}
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
