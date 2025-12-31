// src/app/features/shop/ProductDetailPage.jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  ShoppingCart, ShieldCheck, Truck, Clock, 
  Info, Ruler, Layers, CheckCircle 
} from 'lucide-react';
import clsx from 'clsx';

// Services & Hooks
import { shopService } from '../../services/shopService';
import { cartService } from '../../services/cartService';
import { useProductCalculator } from './hooks/useProductCalculator';

// نکته: کامپوننت‌های ProductGallery و PriceCard در انتهای همین فایل تعریف شده‌اند
// بنابراین نیازی به ایمپورت آن‌ها نیست.

const ProductDetailPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  // ۱. دریافت اطلاعات محصول
  const { data, isLoading, error } = useQuery({
    queryKey: ['product-detail', slug],
    queryFn: () => shopService.getProductDetail(slug),
    retry: 1,
  });

  // فراخوانی هوک محاسبات
  const { state, setters, pricing } = useProductCalculator(data);

  // ۲. هندل کردن افزودن به سبد
  const addToCartMutation = useMutation({
    mutationFn: cartService.addToCart,
    onSuccess: () => {
      toast.success('محصول با موفقیت به سبد خرید اضافه شد');
      navigate('/cart'); // یا باز کردن دراور سبد خرید
    },
    onError: (err) => {
      toast.error('خطا در افزودن به سبد خرید');
      console.error(err);
    }
  });

  const handleAddToCart = () => {
    // اعتبارسنجی ساده
    if (data.pricing_config?.allow_custom_quantity && state.customQuantity < data.pricing_config.min_quantity) {
      toast.error(`حداقل تعداد سفارش ${data.pricing_config.min_quantity} عدد است`);
      return;
    }

    // ساخت پیلود طبق مستندات
    const payload = {
      product_id: data.product_info.id,
      selections: {
        name: data.product_info.name, 
        // منطق ارسال تعداد
        ...(state.quantityType === 'fixed' 
            ? { quantity_id: state.selectedQuantityId } 
            : { quantity: state.customQuantity }),
        
        // منطق سایز
        ...(state.sizeType === 'fixed'
            ? { size_id: state.selectedSizeId }
            : { custom_size: state.customDimensions }), 

        options: state.selectedOptions,
      }
    };
    
    addToCartMutation.mutate(payload);
  };

  // لودینگ
  if (isLoading) return <ProductDetailSkeleton />;
  if (error) return <div className="text-center py-20 text-red-500">محصول یافت نشد</div>;

  const { product_info, pricing_config, options, sizes, quantities, images } = data;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      
      {/* Breadcrumb */}
      <div className="text-sm breadcrumbs text-gray-500 mb-6">
        <ul>
          <li><a href="/">خانه</a></li>
          <li><a href="/shop">محصولات</a></li>
          {product_info.parent_category && <li>{product_info.parent_category}</li>}
          <li className="font-bold text-primary">{product_info.name}</li>
        </ul>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 relative">
        
        {/* === ستون راست: گالری === */}
        <div className="lg:col-span-4">
           <ProductGallery images={images} />
        </div>

        {/* === ستون وسط: اطلاعات و فرم‌ها === */}
        <div className="lg:col-span-5 flex flex-col gap-8">
          
          {/* 1. اطلاعات اولیه */}
          <div>
            <h1 className="text-2xl md:text-3xl font-black text-gray-800 leading-tight mb-3">
              {product_info.name}
            </h1>
            <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
               <span className="bg-gray-100 px-2 py-1 rounded">کد: {product_info.code}</span>
               {product_info.children_category && (
                 <span className="text-primary font-medium">{product_info.children_category}</span>
               )}
            </div>
            {product_info.description && (
              <p className="text-gray-600 leading-relaxed text-sm text-justify">
                {product_info.description}
              </p>
            )}
          </div>

          <div className="divider my-0"></div>

          {/* 2. فرم سفارش */}
          <div className="flex flex-col gap-6">
            
            {/* انتخاب سایز */}
            <div className="card bg-white border border-base-200 shadow-sm p-4">
              <h3 className="font-bold text-gray-800 flex items-center gap-2 mb-4">
                <Ruler className="text-primary w-5 h-5" />
                انتخاب ابعاد و سایز
              </h3>
              
              <div className="form-control w-full">
                <select 
                  className="select select-bordered w-full"
                  value={state.sizeType === 'fixed' ? state.selectedSizeId : 'custom'}
                  onChange={(e) => {
                    if (e.target.value === 'custom') {
                      setters.setSizeType('custom');
                    } else {
                      setters.setSizeType('fixed');
                      setters.setSelectedSizeId(e.target.value);
                    }
                  }}
                >
                  {sizes.map(size => (
                    <option key={size.id} value={size.id}>
                      {size.label || size.title} {size.price_impact > 0 && `(+${parseInt(size.price_impact).toLocaleString()} IQD)`}
                    </option>
                  ))}
                  {pricing_config.accepts_custom_dimensions && (
                    <option value="custom">ابعاد دلخواه (سفارشی)</option>
                  )}
                </select>

                {state.sizeType === 'custom' && (
                  <div className="grid grid-cols-2 gap-4 mt-3 animate-in fade-in slide-in-from-top-2">
                    <div className="form-control">
                      <label className="label"><span className="label-text text-xs">طول (mm)</span></label>
                      <input 
                        type="number" 
                        className="input input-bordered input-sm" 
                        placeholder={`min: ${pricing_config.min_width}`}
                        value={state.customDimensions.width}
                        onChange={(e) => setters.setCustomDimensions({...state.customDimensions, width: e.target.value})}
                      />
                    </div>
                    <div className="form-control">
                      <label className="label"><span className="label-text text-xs">عرض (mm)</span></label>
                      <input 
                        type="number" 
                        className="input input-bordered input-sm" 
                        placeholder={`max: ${pricing_config.max_width}`}
                        value={state.customDimensions.height}
                        onChange={(e) => setters.setCustomDimensions({...state.customDimensions, height: e.target.value})}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* انتخاب تعداد */}
            <div className="card bg-white border border-base-200 shadow-sm p-4">
              <h3 className="font-bold text-gray-800 flex items-center gap-2 mb-4">
                <Layers className="text-primary w-5 h-5" />
                تعداد سفارش
              </h3>

              {quantities && quantities.length > 0 ? (
                <select 
                  className="select select-bordered w-full font-bold text-lg"
                  value={state.selectedQuantityId}
                  onChange={(e) => setters.setSelectedQuantityId(e.target.value)}
                >
                  {quantities.map(q => (
                    <option key={q.id} value={q.id}>
                      {q.value.toLocaleString()} عدد
                    </option>
                  ))}
                </select>
              ) : (
                <div className="flex items-center gap-3">
                   <button 
                     className="btn btn-square btn-outline"
                     onClick={() => setters.setCustomQuantity(Math.max(pricing_config.min_quantity, state.customQuantity - 1))}
                   >-</button>
                   <input 
                     type="number" 
                     className="input input-bordered text-center font-bold text-lg flex-1"
                     value={state.customQuantity}
                     onChange={(e) => setters.setCustomQuantity(parseInt(e.target.value) || 0)}
                     min={pricing_config.min_quantity}
                     max={pricing_config.max_quantity}
                   />
                   <button 
                     className="btn btn-square btn-outline"
                     onClick={() => setters.setCustomQuantity(Math.min(pricing_config.max_quantity, state.customQuantity + 1))}
                   >+</button>
                </div>
              )}
              {pricing_config.min_quantity > 1 && (
                 <p className="text-xs text-gray-400 mt-2">حداقل سفارش: {pricing_config.min_quantity} عدد</p>
              )}
            </div>

            {/* آپشن‌ها */}
            {options && options.length > 0 && (
              <div className="card bg-white border border-base-200 shadow-sm p-4">
                <h3 className="font-bold text-gray-800 flex items-center gap-2 mb-4">
                  <CheckCircle className="text-primary w-5 h-5" />
                  ویژگی‌های محصول
                </h3>
                
                <div className="space-y-4">
                  {options.map((opt) => (
                    <div key={opt.id} className="form-control w-full">
                      <div className="label py-1">
                        <span className="label-text font-bold text-gray-700">
                          {opt.label} {opt.is_required && <span className="text-error">*</span>}
                        </span>
                        {opt.guide_text && (
                          <div className="tooltip tooltip-left" data-tip={opt.guide_text}>
                            <Info size={14} className="text-info cursor-pointer" />
                          </div>
                        )}
                      </div>
                      
                      {opt.type === 'select' && (
                        <select 
                          className="select select-bordered select-sm w-full"
                          onChange={(e) => setters.setSelectedOptions({
                            ...state.selectedOptions,
                            [opt.id]: e.target.value
                          })}
                          value={state.selectedOptions[opt.id] || ''}
                        >
                          {!opt.is_required && <option value="">انتخاب کنید...</option>}
                          {opt.choices.map(choice => (
                            <option key={choice.id} value={choice.id}>
                              {choice.label} 
                              {parseInt(choice.price_impact) > 0 ? ` (+${parseInt(choice.price_impact).toLocaleString()})` : ''}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* === ستون چپ: باکس قیمت شناور === */}
        <div className="lg:col-span-3">
          <div className="sticky top-24 space-y-4">
            
            <PriceCard 
              pricing={pricing} 
              isLoading={addToCartMutation.isLoading}
              onAddToCart={handleAddToCart}
            />

            <div className="bg-gray-50 rounded-xl p-4 text-xs text-gray-500 space-y-3 border border-base-200">
              <div className="flex items-center gap-3">
                <ShieldCheck className="text-emerald-500 w-5 h-5 shrink-0" />
                <span>تضمین کیفیت چاپ و متریال</span>
              </div>
              <div className="flex items-center gap-3">
                <Truck className="text-blue-500 w-5 h-5 shrink-0" />
                <span>ارسال سریع به سراسر عراق</span>
              </div>
              <div className="flex items-center gap-3">
                <Clock className="text-orange-500 w-5 h-5 shrink-0" />
                <span>پشتیبانی ۲۴ ساعته آنلاین</span>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

// --- Sub-components Definitions ---

const PriceCard = ({ pricing, isLoading, onAddToCart }) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl border border-primary/10 overflow-hidden">
      <div className="p-5 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <h3 className="text-lg font-bold mb-1">فاکتور نهایی</h3>
        <p className="text-xs opacity-70">محاسبه آنلاین بر اساس انتخاب‌های شما</p>
      </div>
      
      <div className="p-5 space-y-3">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>قیمت واحد پایه:</span>
          <span>{pricing.baseUnitPrice.toLocaleString()}</span>
        </div>
        
        {pricing.extraCosts > 0 && (
          <div className="flex justify-between items-center text-sm text-amber-600 bg-amber-50 px-2 py-1 rounded">
            <span>آپشن‌ها (به هر واحد):</span>
            <span>+ {pricing.extraCosts.toLocaleString()}</span>
          </div>
        )}

        <div className="divider my-1"></div>

        <div className="flex flex-col gap-1">
          <div className="flex justify-between items-center">
            <span className="font-bold text-gray-800">قیمت نهایی:</span>
            <div className="flex items-baseline gap-1 text-primary">
              <span className="text-2xl font-black">
                {pricing.totalPrice.toLocaleString()}
              </span>
              <span className="text-xs font-bold">IQD</span>
            </div>
          </div>
          <p className="text-xs text-gray-400 text-left">
             برای {pricing.finalQuantity.toLocaleString()} عدد
          </p>
        </div>

        <button 
          onClick={onAddToCart}
          disabled={isLoading}
          className="btn btn-primary w-full shadow-lg shadow-primary/30 mt-4 text-lg font-bold"
        >
          {isLoading ? <span className="loading loading-spinner"></span> : (
             <>
               <ShoppingCart size={20} />
               ثبت سفارش
             </>
          )}
        </button>
      </div>
    </div>
  );
};

const ProductGallery = ({ images }) => {
    const [activeImage, setActiveImage] = useState(images?.[0]?.image_url);
  
    return (
      <div className="flex flex-col gap-4">
        <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-gray-100 border border-base-200">
           {activeImage ? (
             <img src={activeImage} className="w-full h-full object-cover" alt="Product" />
           ) : (
             <div className="w-full h-full flex items-center justify-center text-gray-300">تصویر ندارد</div>
           )}
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2">
           {images?.map((img) => (
             <button 
               key={img.id} 
               onClick={() => setActiveImage(img.image_url)}
               className={clsx(
                 "w-20 h-20 rounded-lg overflow-hidden border-2 flex-shrink-0 transition-all",
                 activeImage === img.image_url ? "border-primary p-0.5" : "border-transparent opacity-70 hover:opacity-100"
               )}
             >
               <img src={img.image_url} className="w-full h-full object-cover rounded-md" alt="Thumb" />
             </button>
           ))}
        </div>
      </div>
    );
};

const ProductDetailSkeleton = () => (
    <div className="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 aspect-square bg-gray-200 rounded-2xl animate-pulse"></div>
        <div className="lg:col-span-5 space-y-4">
            <div className="h-8 w-3/4 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-4 w-1/2 bg-gray-200 rounded animate-pulse"></div>
            <div className="h-32 w-full bg-gray-200 rounded animate-pulse mt-8"></div>
        </div>
        <div className="lg:col-span-3 h-64 bg-gray-200 rounded-2xl animate-pulse"></div>
    </div>
);

export default ProductDetailPage;