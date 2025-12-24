// src/app/features/admin/products/ProductDetailPage.jsx
import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Edit, Trash2, Box, Layers, Ruler, 
  DollarSign, CheckCircle2, XCircle, Info, Image as ImageIcon,
  MoreVertical, Calendar, Globe
} from 'lucide-react';
import { adminProductService } from '../../services/adminProductService';
import { adminCategoryService } from '../../services/adminCategoryService';

const ProductDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // 1. دریافت اطلاعات محصول
  const { data: product, isLoading } = useQuery({
    queryKey: ['admin-product', id],
    queryFn: () => adminProductService.getById(id),
  });

  // 2. دریافت نام دسته‌بندی (چون در محصول معمولاً ID ذخیره می‌شود)
  const { data: categories } = useQuery({
    queryKey: ['admin-categories'],
    queryFn: adminCategoryService.getAll,
    enabled: !!product,
  });

  const categoryName = categories?.find(c => c.id === product?.shell?.category)?.name;

  if (isLoading) return (
    <div className="h-screen flex flex-col items-center justify-center gap-4">
       <span className="loading loading-spinner loading-lg text-primary"></span>
       <p className="text-slate-400 font-medium">در حال بارگذاری اطلاعات محصول...</p>
    </div>
  );

  if (!product) return <div className="text-center p-20 text-slate-400">محصول یافت نشد :(</div>;

  const { shell, pricing_config, quantities, sizes, images, options } = product;

  // فرمت قیمت
  const formatPrice = (p) => new Intl.NumberFormat('fa-IQ').format(Number(p));

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 pb-24">
      
      {/* --- HEADER --- */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4 border-b border-slate-200 pb-6">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/products')} className="btn btn-circle btn-ghost btn-sm text-slate-500">
             <ArrowRight size={22}/>
          </button>
          <div className="flex gap-5 items-center">
              {/* آواتار محصول */}
              <div className="avatar">
                  <div className="w-24 h-24 rounded-2xl ring-4 ring-white shadow-lg bg-slate-100 overflow-hidden">
                      {images && images.length > 0 ? (
                          <img src={images[0].image} alt={shell.name} className="object-cover w-full h-full"/>
                      ) : (
                          <div className="w-full h-full flex items-center justify-center text-slate-300">
                             <Box size={32}/>
                          </div>
                      )}
                  </div>
              </div>
              
              <div>
                  <div className="flex items-center gap-3">
                     <h1 className="text-3xl font-black text-slate-800">{shell.name}</h1>
                     {shell.is_active ? (
                        <div className="badge badge-success gap-1 text-white shadow-success/30 shadow-lg py-3 px-3">
                           <CheckCircle2 size={14}/> فعال
                        </div>
                     ) : (
                        <div className="badge badge-error gap-1 text-white shadow-error/30 shadow-lg py-3 px-3">
                           <XCircle size={14}/> غیرفعال
                        </div>
                     )}
                  </div>
                  
                  <div className="flex items-center gap-3 mt-2 text-sm text-slate-500 font-medium">
                      <span className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded-lg">
                         <Layers size={14}/> {categoryName || 'بدون دسته‌بندی'}
                      </span>
                      <span className="flex items-center gap-1 font-mono dir-ltr bg-slate-100 px-2 py-1 rounded-lg">
                         <span className="text-slate-400">SKU:</span> {shell.code || '---'}
                      </span>
                  </div>
              </div>
          </div>
        </div>

        <div className="flex gap-2">
           <Link to={`/admin/products/edit/${id}`} className="btn btn-primary px-6 shadow-xl shadow-primary/20 gap-2 rounded-xl">
              <Edit size={18}/> ویرایش محصول
           </Link>
           <button className="btn btn-square btn-ghost text-slate-400">
              <MoreVertical size={20}/>
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* === ستون اصلی (چپ) === */}
          <div className="lg:col-span-2 space-y-8">
              
              {/* 1. Basic Info Card */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-10 -mt-10 blur-2xl"></div>
                  
                  <h3 className="font-bold text-slate-800 text-lg mb-4 flex items-center gap-2">
                     <Info size={20} className="text-primary"/> درباره محصول
                  </h3>
                  <p className="text-slate-600 leading-8 text-justify bg-slate-50/50 p-4 rounded-2xl border border-slate-50">
                      {shell.description || 'توضیحاتی برای این محصول ثبت نشده است.'}
                  </p>

                  <div className="mt-6 flex flex-wrap gap-4">
                      {shell.slug && (
                         <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-4 py-2 rounded-xl border border-blue-100">
                            <Globe size={16}/>
                            <span className="font-mono dir-ltr">printoo24.com/product/{shell.slug}</span>
                         </div>
                      )}
                  </div>
              </div>

              {/* 2. Pricing & Quantities */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                  <div className="flex justify-between items-center mb-6">
                     <h3 className="font-bold text-slate-800 text-lg flex items-center gap-2">
                        <DollarSign size={20} className="text-emerald-500"/> 
                        {shell.has_quantity ? 'لیست قیمت تیراژها' : 'محاسبه قیمت (متری/تعدادی)'}
                     </h3>
                     {pricing_config.base_setup_price > 0 && (
                        <div className="badge badge-ghost py-3">
                           هزینه ثابت: {formatPrice(pricing_config.base_setup_price)} IQD
                        </div>
                     )}
                  </div>

                  {shell.has_quantity ? (
                      /* جدول تیراژ (افست) */
                      quantities && quantities.length > 0 ? (
                          <div className="overflow-x-auto">
                              <table className="table w-full">
                                  <thead className="bg-slate-50 text-slate-500">
                                      <tr>
                                          <th>تیراژ (تعداد)</th>
                                          <th>قیمت کل (IQD)</th>
                                          <th>قیمت واحد</th>
                                          <th>توضیحات</th>
                                      </tr>
                                  </thead>
                                  <tbody>
                                      {quantities.map((q, idx) => (
                                          <tr key={idx} className="hover:bg-slate-50">
                                              <td className="font-bold font-mono text-lg">{q.value}</td>
                                              <td className="text-emerald-600 font-bold dir-ltr text-right text-lg">{formatPrice(q.price)}</td>
                                              <td className="text-slate-400 font-mono text-xs dir-ltr text-right">
                                                  ~ {formatPrice(Math.round(q.price / q.value))}
                                              </td>
                                              <td>{q.guide_text || '-'}</td>
                                          </tr>
                                      ))}
                                  </tbody>
                              </table>
                          </div>
                      ) : <div className="text-center py-8 text-slate-400 border border-dashed rounded-xl">هیچ تیراژی تعریف نشده است</div>
                  ) : (
                      /* بنر / دیجیتال */
                      <div className="bg-amber-50 border border-amber-100 p-6 rounded-2xl text-amber-800">
                          <p className="font-bold mb-2">این محصول بر اساس متراژ یا تعداد دلخواه محاسبه می‌شود.</p>
                          <ul className="list-disc list-inside text-sm space-y-1 opacity-80">
                              <li>قیمت پایه: {formatPrice(shell.price)} IQD</li>
                              <li>حداقل سفارش: {pricing_config.min_quantity || 1} عدد</li>
                              {pricing_config.design_service_available && (
                                  <li>هزینه طراحی: {formatPrice(pricing_config.design_fee)} IQD</li>
                              )}
                          </ul>
                      </div>
                  )}
              </div>

              {/* 3. Features & Options */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
                  <h3 className="font-bold text-slate-800 text-lg mb-6 flex items-center gap-2">
                     <Layers size={20} className="text-purple-500"/> ویژگی‌های انتخابی
                  </h3>
                  
                  {options && options.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {options.map((opt, idx) => (
                              <div key={idx} className="border border-slate-200 rounded-2xl p-4 hover:border-purple-200 transition-colors">
                                  <div className="flex justify-between items-center mb-3">
                                      <span className="font-bold text-slate-700">{opt.label}</span>
                                      {opt.is_required && <span className="badge badge-xs badge-error badge-outline">اجباری</span>}
                                  </div>
                                  <div className="flex flex-wrap gap-2">
                                      {opt.values_config?.map((val, vIdx) => (
                                          <span key={vIdx} className="badge badge-ghost bg-slate-100 text-xs py-3">
                                              {val.label}
                                              {val.price_impact > 0 && (
                                                  <span className="text-emerald-600 mr-1 text-[10px]">
                                                      (+{formatPrice(val.price_impact)})
                                                  </span>
                                              )}
                                          </span>
                                      ))}
                                  </div>
                              </div>
                          ))}
                      </div>
                  ) : (
                      <div className="text-center py-8 text-slate-400 border border-dashed rounded-xl">هیچ ویژگی انتخابی (مثل رنگ یا جنس) تعریف نشده است.</div>
                  )}
              </div>

          </div>

          {/* === ستون کناری (راست) === */}
          <div className="space-y-6">
              
              {/* Sizes Card */}
              <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm">
                  <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                      <Ruler size={18} className="text-slate-400"/> سایزهای استاندارد
                  </h3>
                  {sizes && sizes.length > 0 ? (
                      <div className="space-y-2">
                          {sizes.map((s, idx) => (
                              <div key={idx} className="flex justify-between items-center bg-slate-50 p-3 rounded-xl">
                                  <span className="font-bold text-sm">{s.name}</span>
                                  <span className="font-mono text-xs text-slate-500 dir-ltr">{s.width} × {s.height} cm</span>
                              </div>
                          ))}
                      </div>
                  ) : (
                      <div className="text-xs text-slate-400 text-center">سایز ثابت تعریف نشده (سایز آزاد)</div>
                  )}
              </div>

              {/* Gallery Preview */}
              <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm">
                  <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                      <ImageIcon size={18} className="text-slate-400"/> گالری تصاویر
                  </h3>
                  <div className="grid grid-cols-3 gap-2">
                      {images?.slice(0, 6).map((img, idx) => (
                          <div key={idx} className="aspect-square rounded-xl overflow-hidden border border-slate-100 relative group cursor-pointer">
                              <img src={img.image} alt="" className="w-full h-full object-cover transition-transform group-hover:scale-110"/>
                              {idx === 0 && <span className="absolute bottom-1 right-1 bg-warning text-[8px] px-1 rounded font-bold">کاور</span>}
                          </div>
                      ))}
                      {(!images || images.length === 0) && (
                          <div className="col-span-3 text-center py-4 text-xs text-slate-400 bg-slate-50 rounded-xl">بدون تصویر</div>
                      )}
                  </div>
              </div>

              {/* Meta Info */}
              <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm space-y-3">
                  <div className="flex justify-between text-xs text-slate-500">
                      <span className="flex items-center gap-2"><Calendar size={14}/> تاریخ ایجاد:</span>
                      <span className="dir-ltr font-mono">{new Date(product.created_at || Date.now()).toLocaleDateString('fa-IR')}</span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-500">
                      <span className="flex items-center gap-2"><Edit size={14}/> آخرین ویرایش:</span>
                      <span className="dir-ltr font-mono">{new Date(product.updated_at || Date.now()).toLocaleDateString('fa-IR')}</span>
                  </div>
              </div>

          </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;