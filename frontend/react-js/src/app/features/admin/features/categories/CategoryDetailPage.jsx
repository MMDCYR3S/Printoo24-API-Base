// src/app/features/admin/categories/CategoryDetailPage.jsx
import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Edit, Calendar, Info, CheckCircle2, XCircle, 
  CornerUpRight, Image as ImageIcon, Box, Layers, Package 
} from 'lucide-react';
import { adminCategoryService } from '../../services/adminCategoryService';
import clsx from 'clsx';

const CategoryDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // دریافت اطلاعات کامل دسته
  const { data: category, isLoading } = useQuery({
    queryKey: ['category-detail', id],
    queryFn: () => adminCategoryService.getById(id),
  });

  if (isLoading) return (
    <div className="h-screen flex items-center justify-center flex-col gap-4">
        <span className="loading loading-spinner loading-lg text-primary"></span>
        <span className="text-slate-400 font-medium">در حال دریافت اطلاعات...</span>
    </div>
  );

  if (!category) return (
    <div className="text-center py-20 text-slate-400">دسته‌بندی یافت نشد.</div>
  );

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto pb-32 animate-fade-in space-y-8">
      
      {/* --- Header --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
            <button onClick={() => navigate('/admin/categories')} className="btn btn-circle btn-ghost btn-sm">
                <ArrowRight size={20} />
            </button>
            <div>
                <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-black text-slate-800">{category.name}</h1>
                    {category.is_active ? (
                        <span className="badge badge-success badge-sm gap-1 text-white"><CheckCircle2 size={12}/> فعال</span>
                    ) : (
                        <span className="badge badge-error badge-sm gap-1 text-white"><XCircle size={12}/> غیرفعال</span>
                    )}
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400 mt-2 font-mono dir-ltr">
                    <span>ID: {category.id}</span>
                    <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                    <span>/{category.slug}</span>
                </div>
            </div>
        </div>
        
        <Link to={`/admin/categories/edit/${category.id}`} className="btn btn-primary px-6 shadow-lg shadow-primary/30">
            <Edit size={18}/> ویرایش دسته
        </Link>
      </div>

      {/* --- Top Info Grid --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Col 1: Description & Parent */}
          <div className="lg:col-span-2 space-y-6">
              {/* Parent Info */}
              {category.parent && (
                  <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-2xl flex items-center gap-3 text-indigo-800">
                      <CornerUpRight size={20} className="text-indigo-500"/>
                      <span className="text-sm font-bold">زیرمجموعه‌ی:</span>
                      <Link to={`/admin/categories/${category.parent}`} className="link link-hover font-black text-lg">
                          {category.parent_name}
                      </Link>
                  </div>
              )}

              {/* Description */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-2 h-full bg-primary/80"></div>
                  <h3 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                      <Info size={18} className="text-slate-400"/> توضیحات
                  </h3>
                  <p className="text-slate-600 leading-7 text-sm text-justify">
                      {category.description || 'توضیحات ثبت نشده است.'}
                  </p>
                  
                  <div className="mt-6 pt-4 border-t border-slate-50 flex items-center gap-4 text-xs text-slate-400">
                      <div className="flex items-center gap-1">
                          <Calendar size={14}/> ایجاد: <span className="dir-ltr font-mono">{new Date(category.created_at).toLocaleDateString('fa-IR')}</span>
                      </div>
                      <div className="flex items-center gap-1">
                          <Calendar size={14}/> بروزرسانی: <span className="dir-ltr font-mono">{new Date(category.updated_at).toLocaleDateString('fa-IR')}</span>
                      </div>
                  </div>
              </div>
          </div>

          {/* Col 2: Images */}
          <div className="space-y-4">
              <div className="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
                  <h3 className="text-xs font-bold text-slate-400 mb-2 uppercase">تصویر باکس (Box)</h3>
                  <div className="aspect-square bg-slate-50 rounded-2xl overflow-hidden border border-slate-100 flex items-center justify-center">
                      {category.banner_box ? (
                          <img src={category.banner_box} alt="Box" className="w-full h-full object-cover"/>
                      ) : (
                          <div className="text-slate-300 flex flex-col items-center gap-2"><Box size={40}/><span className="text-xs">ندارد</span></div>
                      )}
                  </div>
              </div>
              
              <div className="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm">
                  <h3 className="text-xs font-bold text-slate-400 mb-2 uppercase">بنر عریض (Wide)</h3>
                  <div className="aspect-[3/1] bg-slate-50 rounded-2xl overflow-hidden border border-slate-100 flex items-center justify-center">
                      {category.banner_wide ? (
                          <img src={category.banner_wide} alt="Wide" className="w-full h-full object-cover"/>
                      ) : (
                          <div className="text-slate-300 flex flex-col items-center gap-2"><ImageIcon size={30}/><span className="text-xs">ندارد</span></div>
                      )}
                  </div>
              </div>
          </div>
      </div>

      {/* --- Section: Subcategories --- */}
      {category.children && category.children.length > 0 && (
          <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-800 font-black text-xl">
                  <Layers className="text-primary"/>
                  <h2>زیرمجموعه‌ها ({category.children.length})</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {category.children.map(child => (
                      <div key={child.id} className="bg-white rounded-3xl border border-slate-100 shadow-sm hover:shadow-lg transition-all p-5 flex flex-col group">
                          <div className="flex justify-between items-start mb-4">
                              <Link to={`/admin/categories/${child.id}`} className="font-bold text-lg text-slate-700 hover:text-primary transition-colors flex items-center gap-2">
                                  {child.name}
                                  <ArrowRight size={16} className="-rotate-45 opacity-0 group-hover:opacity-100 transition-opacity text-primary"/>
                              </Link>
                              <Link to={`/admin/categories/edit/${child.id}`} className="btn btn-xs btn-ghost text-slate-300 hover:text-blue-500">
                                  <Edit size={14}/>
                              </Link>
                          </div>
                          
                          {/* Products Preview for Subcategory */}
                          <div className="bg-slate-50 rounded-2xl p-3 mt-auto">
                              <div className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-wider flex justify-between">
                                  <span>محصولات اخیر</span>
                                  {child.products?.length > 0 && <span>{child.products.length} مورد</span>}
                              </div>
                              {child.products && child.products.length > 0 ? (
                                  <div className="flex -space-x-3 space-x-reverse overflow-hidden py-1">
                                      {child.products.slice(0, 4).map(prod => (
                                          <div key={prod.id} className="w-10 h-10 rounded-full ring-2 ring-white bg-white relative tooltip tooltip-top" data-tip={prod.name}>
                                              <img 
                                                src={prod.image_url || '/placeholder.png'} 
                                                alt={prod.name} 
                                                className="w-full h-full object-cover rounded-full"
                                                onError={e => e.target.src = 'https://via.placeholder.com/40'}
                                              />
                                          </div>
                                      ))}
                                      {child.products.length > 4 && (
                                          <div className="w-10 h-10 rounded-full ring-2 ring-white bg-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-500">
                                              +{child.products.length - 4}
                                          </div>
                                      )}
                                  </div>
                              ) : (
                                  <div className="text-center text-xs text-slate-300 py-2">بدون محصول</div>
                              )}
                          </div>
                      </div>
                  ))}
              </div>
          </div>
      )}

      {/* --- Section: Direct Products --- */}
      {category.products && category.products.length > 0 && (
          <div className="space-y-4 pt-6 border-t border-dashed border-slate-200">
              <div className="flex items-center gap-2 text-slate-800 font-black text-xl">
                  <Package className="text-emerald-500"/>
                  <h2>محصولات مستقیم ({category.products.length})</h2>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                  {category.products.map(product => (
                      <Link 
                        key={product.id} 
                        to={`/admin/products/edit/${product.id}`}
                        className="bg-white p-3 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all group"
                      >
                          <div className="aspect-square bg-slate-50 rounded-xl overflow-hidden mb-3 relative">
                              <img 
                                src={product.image_url || '/placeholder.png'} 
                                alt={product.name} 
                                className="w-full h-full object-cover"
                                onError={e => e.target.src = 'https://via.placeholder.com/150'}
                              />
                              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                  <span className="text-white text-xs font-bold border border-white/50 px-3 py-1 rounded-full backdrop-blur-sm">ویرایش</span>
                              </div>
                          </div>
                          <h4 className="font-bold text-slate-700 text-sm line-clamp-1 mb-1 group-hover:text-primary transition-colors">{product.name}</h4>
                          <div className="flex justify-between items-center">
                              <span className="text-[10px] font-mono text-slate-400">/{product.slug}</span>
                              <span className="text-xs font-bold text-emerald-600">{product.price_display}</span>
                          </div>
                      </Link>
                  ))}
              </div>
          </div>
      )}
      
      {/* Empty State for Leaf Category */}
      {(!category.children?.length && !category.products?.length) && (
          <div className="text-center py-16 bg-white rounded-[3rem] border-2 border-dashed border-slate-100">
              <div className="w-16 h-16 bg-slate-50 text-slate-300 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Package size={32}/>
              </div>
              <h3 className="text-slate-500 font-bold mb-2">این دسته‌بندی خالی است</h3>
              <p className="text-slate-400 text-sm mb-6">هیچ زیرمجموعه یا محصول مستقیمی در آن وجود ندارد.</p>
              <Link to={`/admin/products/create?category=${category.id}`} className="btn btn-outline btn-primary btn-sm">
                  افزودن محصول جدید
              </Link>
          </div>
      )}

    </div>
  );
};

export default CategoryDetailPage;