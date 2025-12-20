// src/app/features/admin/categories/CategoryDetailPage.jsx
import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Edit, Calendar, Link as LinkIcon, CheckCircle2, XCircle, FolderOpen } from 'lucide-react';
import { adminCategoryService } from '../../services/adminCategoryService';
import clsx from 'clsx';

const CategoryDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: category, isLoading } = useQuery({
    queryKey: ['category', id],
    queryFn: () => adminCategoryService.getById(id),
  });

  if (isLoading) return <div className="h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (!category) return <div className="text-center p-10">دسته یافت نشد</div>;

  return (
    <div className="p-6 md:p-10 max-w-6xl mx-auto space-y-8 animate-fade-in-up">
      
      {/* --- HEADER --- */}
      <div className="flex flex-col md:flex-row justify-between items-start gap-4 border-b border-base-200 pb-6">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/admin/categories')} className="btn btn-circle btn-ghost btn-sm">
             <ArrowRight size={22}/>
          </button>
          <div className="flex gap-4 items-center">
              {/* آواتار بزرگ */}
              <div className="avatar">
                  <div className="w-20 h-20 rounded-2xl ring-2 ring-slate-100 shadow-md">
                      {category.banner_box ? (
                          <img src={category.banner_box} alt={category.name} />
                      ) : (
                          <div className="bg-slate-100 w-full h-full flex items-center justify-center text-slate-300">
                             <FolderOpen size={32}/>
                          </div>
                      )}
                  </div>
              </div>
              <div>
                  <h1 className="text-3xl font-black text-slate-800">{category.name}</h1>
                  <div className="flex items-center gap-3 mt-2">
                      <span className="badge badge-ghost font-mono dir-ltr opacity-70">/{category.slug}</span>
                      {category.is_active ? (
                          <span className="badge badge-success badge-outline gap-1 text-xs font-bold"><CheckCircle2 size={12}/> فعال</span>
                      ) : (
                          <span className="badge badge-error badge-outline gap-1 text-xs font-bold"><XCircle size={12}/> غیرفعال</span>
                      )}
                  </div>
              </div>
          </div>
        </div>

        <Link to={`/admin/categories/edit/${category.id}`} className="btn btn-primary px-6 shadow-lg shadow-primary/20">
           <Edit size={18}/> ویرایش دسته
        </Link>
      </div>

      {/* --- CONTENT GRID --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          {/* Main Info */}
          <div className="md:col-span-2 space-y-8">
              
              {/* Description */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-primary"></div>
                  <h3 className="font-bold text-slate-800 text-lg mb-4">توضیحات</h3>
                  <p className="text-slate-600 leading-relaxed text-justify">
                      {category.description || 'بدون توضیحات...'}
                  </p>
              </div>

              {/* Children List (Sub-categories) */}
              <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                      <h3 className="font-bold text-slate-800 text-lg">زیرمجموعه‌ها</h3>
                      <span className="badge badge-neutral">{category.children?.length || 0}</span>
                  </div>
                  
                  {category.children && category.children.length > 0 ? (
                      <div className="divide-y divide-slate-50">
                          {category.children.map(child => (
                              <div key={child.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors group">
                                  <div className="flex items-center gap-3">
                                      <div className="w-10 h-10 rounded-lg bg-slate-100 overflow-hidden">
                                          {/* در API شما، چیلدرن فقط id و name دارد، شاید عکس نداشته باشد */}
                                          <FolderOpen className="w-full h-full p-2 text-slate-300"/> 
                                      </div>
                                      <span className="font-bold text-slate-700">{child.name}</span>
                                  </div>
                                  <Link 
                                    to={`/admin/categories/${child.id}`} 
                                    className="btn btn-ghost btn-sm text-primary opacity-0 group-hover:opacity-100 transition-all"
                                  >
                                    مشاهده
                                  </Link>
                              </div>
                          ))}
                      </div>
                  ) : (
                      <div className="p-10 text-center text-slate-400 text-sm">
                          هیچ زیرمجموعه‌ای یافت نشد.
                      </div>
                  )}
              </div>
          </div>

          {/* Sidebar Info */}
          <div className="space-y-6">
              {/* Parent Info */}
              <div className="bg-slate-50 p-6 rounded-3xl border border-slate-200">
                  <h4 className="text-xs font-bold text-slate-400 uppercase mb-4">دسته مادر</h4>
                  {category.parent ? (
                      <Link to={`/admin/categories/${category.parent}`} className="flex items-center gap-3 p-3 bg-white rounded-xl shadow-sm hover:shadow-md transition-all">
                          <div className="bg-primary/10 p-2 rounded-lg text-primary">
                              <FolderOpen size={20}/>
                          </div>
                          <div>
                              <div className="font-bold text-slate-700 text-sm">{category.parent_name}</div>
                              <div className="text-[10px] text-slate-400">والد</div>
                          </div>
                      </Link>
                  ) : (
                      <div className="text-sm font-medium text-slate-500 flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-primary"></span>
                          دسته اصلی (ریشه)
                      </div>
                  )}
              </div>

              {/* Wide Banner Preview */}
              {category.banner_wide && (
                  <div className="rounded-3xl overflow-hidden shadow-md ring-4 ring-white">
                      <img src={category.banner_wide} alt="Wide Banner" className="w-full h-auto object-cover" />
                      <div className="bg-white p-3 text-center text-xs text-slate-400 font-bold">بنر عریض</div>
                  </div>
              )}

              {/* Meta Info */}
              <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm space-y-4">
                  <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500 flex items-center gap-2"><Calendar size={14}/> تاریخ ایجاد:</span>
                      <span className="font-mono dir-ltr text-slate-700">
                        {new Date(category.created_at).toLocaleDateString('fa-IR')}
                      </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500 flex items-center gap-2"><Calendar size={14}/> آخرین ویرایش:</span>
                      <span className="font-mono dir-ltr text-slate-700">
                        {new Date(category.updated_at).toLocaleDateString('fa-IR')}
                      </span>
                  </div>
              </div>
          </div>
      </div>
    </div>
  );
};

export default CategoryDetailPage;