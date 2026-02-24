// src/app/features/admin/categories/components/SubCategoryTable.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Edit, Trash2, Eye, ChevronDown, ChevronUp, 
  Package, Image as ImageIcon, CornerDownRight, Box 
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminCategoryService } from '../../../services/adminCategoryService';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const SubCategoryTable = () => {
  const queryClient = useQueryClient();
  const [expandedId, setExpandedId] = useState(null);

  // دریافت لیست زیردسته‌ها + محصولات
  const { data: subCategories = [], isLoading } = useQuery({
    queryKey: ['admin-subcategories-full'],
    queryFn: adminCategoryService.getAllSubCategories,
    staleTime: 1000 * 60 * 2,
  });

  const deleteMutation = useMutation({
    mutationFn: adminCategoryService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['admin-subcategories-full']);
      toast.success('زیردسته حذف شد');
    },
    onError: () => toast.error('خطا در حذف'),
  });

  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این زیردسته اطمینان دارید؟')) {
      deleteMutation.mutate(id);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
        <span className="loading loading-spinner loading-lg text-primary"></span>
        <span className="text-slate-400 font-medium">در حال دریافت زیردسته‌ها و محصولات...</span>
    </div>
  );

  if (subCategories.length === 0) return (
    <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-300">
         <div className="bg-slate-50 inline-flex p-4 rounded-full mb-4 text-slate-400"><Package size={40}/></div>
         <p className="text-slate-500 font-bold">هیچ زیردسته‌ای یافت نشد.</p>
    </div>
  );

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="table w-full">
          <thead className="bg-slate-50/80 text-xs uppercase font-bold text-slate-500">
            <tr>
              <th className="w-12"></th> {/* Toggle Button */}
              <th className="w-16">تصویر</th>
              <th>نام زیردسته</th>
              <th>دسته مادر (والد)</th>
              <th className="text-center">محصولات</th>
              <th className="text-center">وضعیت</th>
              <th className="text-left pl-6">عملیات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {subCategories.map((cat) => {
              const productCount = cat.products?.length || 0;
              const isExpanded = expandedId === cat.id;

              return (
                <React.Fragment key={cat.id}>
                  {/* --- سطر اصلی (SubCategory) --- */}
                  <tr 
                    className={clsx(
                        "hover:bg-blue-50/30 transition-colors cursor-pointer group",
                        isExpanded && "bg-blue-50/50"
                    )}
                    onClick={() => toggleExpand(cat.id)}
                  >
                    {/* Expand Toggle */}
                    <td className="text-center">
                        <button className={clsx("btn btn-xs btn-circle btn-ghost transition-transform", isExpanded && "rotate-180")}>
                            <ChevronDown size={16} className="text-slate-400"/>
                        </button>
                    </td>

                    {/* Image */}
                    <td>
                      <div className="avatar">
                        <div className="w-10 h-10 rounded-lg ring-1 ring-slate-100 bg-white p-0.5">
                          {cat.banners?.box ? (
                            <img src={cat.banners.box} alt={cat.name} className="object-cover rounded-md" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-slate-300"><ImageIcon size={16}/></div>
                          )}
                        </div>
                      </div>
                    </td>
                    
                    {/* Name & Slug */}
                    <td>
                      <div className="font-bold text-slate-700 text-sm">{cat.name}</div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5 dir-ltr text-right truncate max-w-[120px]">
                        /{cat.slug}
                      </div>
                    </td>

                    {/* Parent */}
                    <td>
                        {cat.parent ? (
                            <Link 
                                to={`/admin/categories/${cat.parent.id}`}
                                onClick={(e) => e.stopPropagation()} 
                                className="badge badge-ghost gap-1 text-xs bg-indigo-50 text-indigo-700 border-indigo-100 hover:bg-indigo-100"
                            >
                                <CornerDownRight size={12}/>
                                {cat.parent.name}
                            </Link>
                        ) : (
                            <span className="text-xs text-error opacity-50">-- بدون والد --</span>
                        )}
                    </td>

                    {/* Product Count Badge */}
                    <td className="text-center">
                        <span className={clsx("badge border-0 text-xs font-mono", productCount > 0 ? "bg-primary/10 text-primary" : "bg-slate-100 text-slate-400")}>
                            {productCount}
                        </span>
                    </td>

                    {/* Status */}
                    <td className="text-center">
                        <span className={clsx("w-2 h-2 rounded-full inline-block mr-2", cat.is_active ? "bg-emerald-500" : "bg-red-400")}></span>
                        <span className="text-xs text-slate-500">{cat.is_active ? 'فعال' : 'غیرفعال'}</span>
                    </td>

                    {/* Actions */}
                    <td>
                      <div className="flex justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                        <Link to={`/admin/categories/edit/${cat.id}`} className="btn btn-xs btn-ghost btn-square text-slate-400 hover:text-blue-600">
                            <Edit size={16} />
                        </Link>
                        <button onClick={() => handleDelete(cat.id)} className="btn btn-xs btn-ghost btn-square text-slate-400 hover:text-red-500">
                            <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>

                  {/* --- سطر آکاردئون (محصولات) --- */}
                  <AnimatePresence>
                    {isExpanded && (
                        <tr>
                            <td colSpan="7" className="p-0 border-0">
                                <motion.div 
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    className="bg-slate-50 border-y border-slate-100 shadow-inner overflow-hidden"
                                >
                                    <div className="py-4 pr-16 pl-6">
                                        <div className="flex items-center gap-2 mb-3 text-xs font-bold text-slate-400 uppercase tracking-wider">
                                            <Box size={14}/> لیست محصولات ({productCount})
                                        </div>
                                        
                                        {productCount === 0 ? (
                                            <div className="text-sm text-slate-400 italic bg-white/50 p-4 rounded-xl text-center border border-dashed border-slate-200">
                                                هیچ محصولی در این دسته‌بندی وجود ندارد.
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                                                {cat.products.map(product => (
                                                    <div key={product.id} className="flex items-center gap-3 bg-white p-2 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                                                        {/* Product Image */}
                                                        <div className="w-10 h-10 rounded-lg bg-slate-100 flex-shrink-0">
                                                            <img 
                                                                src={product.image_url || '/placeholder.png'} 
                                                                alt={product.name}
                                                                className="w-full h-full object-cover rounded-lg"
                                                                onError={(e) => { e.target.src = 'https://via.placeholder.com/40'; }} 
                                                            />
                                                        </div>
                                                        {/* Product Info */}
                                                        <div className="flex-1 min-w-0">
                                                            <div className="text-xs font-bold text-slate-700 truncate" title={product.name}>
                                                                {product.name}
                                                            </div>
                                                            <div className="flex justify-between items-center mt-1">
                                                                <span className="text-[10px] font-mono bg-slate-100 px-1 rounded text-slate-500">/{product.slug}</span>

                                                            </div>
                                                        </div>
                                                        {/* Link to Product */}
                                                        <Link 
                                                            to={`/admin/products/edit/${product.id}`} 
                                                            className="btn btn-xs btn-ghost btn-square text-slate-300 hover:text-blue-600"
                                                        >
                                                            <Edit size={12}/>
                                                        </Link>
                                                        <Link 
                                                            to={`/admin/products/${product.id}`} 
                                                            className="btn btn-xs btn-ghost btn-square text-slate-300 hover:text-blue-600"
                                                        >
                                                            <Eye size={12}/>
                                                        </Link>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        
                                        <div className="mt-4 pt-3 border-t border-slate-200 flex justify-end">
                                             <Link to={`/admin/products/create?category=${cat.id}`} className="btn btn-xs btn-outline btn-primary">
                                                 افزودن محصول جدید به این دسته
                                             </Link>
                                        </div>
                                    </div>
                                </motion.div>
                            </td>
                        </tr>
                    )}
                  </AnimatePresence>
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SubCategoryTable;