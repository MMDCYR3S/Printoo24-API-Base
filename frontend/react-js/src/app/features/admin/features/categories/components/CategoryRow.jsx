// src/app/features/admin/categories/components/CategoryRow.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Edit, Trash2, Eye, ChevronDown, ChevronLeft, 
  CornerDownRight, Image as ImageIcon, Box 
} from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

const CategoryRow = ({ 
  category, 
  isSelected, 
  onSelect, 
  onDelete, 
  onToggleStatus 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // بررسی وجود فرزندان در دیتای دریافتی
  const hasChildren = category.children && category.children.length > 0;

  return (
    <>
      {/* --- سطر والد --- */}
      <tr className={clsx("group hover:bg-slate-50 transition-colors border-b border-slate-50", isSelected && "bg-blue-50/50")}>
        {/* Checkbox */}
        <th className="text-center w-12">
          <label>
            <input 
              type="checkbox" 
              className="checkbox checkbox-sm checkbox-primary rounded-md"
              checked={isSelected}
              onChange={() => onSelect(category.id)}
            />
          </label>
        </th>

        {/* Image */}
        <td className="w-20">
          <div className="avatar">
            <div className="w-12 h-12 rounded-xl ring-1 ring-slate-100 bg-white p-0.5">
              {category.banner_box ? (
                <img src={category.banner_box} alt={category.name} className="object-cover rounded-lg" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-300">
                    <ImageIcon size={20}/>
                </div>
              )}
            </div>
          </div>
        </td>

        {/* Name & Accordion Trigger */}
        <td>
          <div className="flex items-center gap-2">
            {/* دکمه بازشو آکاردئون */}
            {hasChildren ? (
                <button 
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="btn btn-xs btn-circle btn-ghost text-slate-400 hover:bg-slate-200 hover:text-slate-700 transition-all"
                >
                    {isExpanded ? <ChevronDown size={16}/> : <ChevronLeft size={16}/>}
                </button>
            ) : (
                <span className="w-6 h-6 inline-block"></span> // فضاسازی برای تراز ماندن
            )}
            
            <div className="flex flex-col">
                <Link to={`edit/${category.id}`} className="font-bold text-slate-700 hover:text-primary transition-colors text-sm">
                    {category.name}
                </Link>
                {hasChildren && (
                    <span className="text-[10px] text-slate-400 mt-0.5">{category.children.length} زیرمجموعه</span>
                )}
            </div>
          </div>
        </td>

        {/* Slug */}
        <td>
          <span className="font-mono text-xs text-slate-400 dir-ltr bg-slate-50 px-2 py-1 rounded">
            /{category.slug}
          </span>
        </td>

        {/* Status */}
        <td className="text-center w-24">
            <button 
                onClick={() => onToggleStatus([category.id], !category.is_active)}
                className={clsx(
                    "badge gap-1 py-3 px-3 border-0 cursor-pointer font-medium text-xs",
                    category.is_active 
                        ? "bg-emerald-50 text-emerald-600 hover:bg-emerald-100" 
                        : "bg-red-50 text-red-600 hover:bg-red-100"
                )}
            >
                {category.is_active ? 'فعال' : 'غیرفعال'}
            </button>
        </td>

        {/* Actions */}
        <td className="w-40">
          <div className="flex justify-end items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
            {/* دکمه دیتیل برای والد */}
            <Link 
                to={`/admin/categories/${category.id}`}
                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-indigo-600 tooltip tooltip-top"
                data-tip="جزئیات"
            >
                <Eye size={16} />
            </Link>
            
            <Link 
                to={`edit/${category.id}`}
                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600 tooltip tooltip-top"
                data-tip="ویرایش"
            >
                <Edit size={16} />
            </Link>

            <button 
                onClick={() => onDelete(category.id)} 
                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500 tooltip tooltip-top"
                data-tip="حذف"
            >
                <Trash2 size={16} />
            </button>
          </div>
        </td>
      </tr>

      {/* --- بخش آکاردئون (فرزندان) --- */}
      <AnimatePresence>
        {isExpanded && hasChildren && (
            <tr>
                <td colSpan="6" className="p-0 border-0">
                    <motion.div 
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="bg-slate-50/50 shadow-inner overflow-hidden"
                    >
                        <div className="pr-16 pl-4 py-4 mr-8 my-2 border-r-2 border-primary/20 space-y-1">
                            {category.children.map(child => (
                                <div key={child.id} className="flex items-center justify-between p-2 hover:bg-white rounded-lg group/sub transition-colors border border-transparent hover:border-slate-100">
                                    <div className="flex items-center gap-3">
                                        <CornerDownRight size={16} className="text-slate-300"/>
                                        
                                        {/* کلیک روی نام زیردسته -> رفتن به دیتیل */}
                                        <Link 
                                            to={`/admin/categories/${child.id}`}
                                            className="font-medium text-slate-600 hover:text-primary text-sm flex items-center gap-2"
                                        >
                                            {child.name}
                                        </Link>
                                        
                                        {child.products && child.products.length > 0 && (
                                            <span className="badge badge-xs bg-slate-100 border-0 text-[10px] text-slate-400">
                                                {child.products.length} محصول
                                            </span>
                                        )}
                                    </div>

                                    {/* عملیات سریع برای زیردسته */}
                                    <div className="flex gap-1 opacity-0 group-hover/sub:opacity-100 transition-opacity">
                                        <Link to={`/admin/categories/${child.id}`} className="btn btn-xs btn-ghost text-indigo-500" title="مشاهده جزئیات">
                                            <Eye size={14}/>
                                        </Link>
                                        <Link to={`edit/${child.id}`} className="btn btn-xs btn-ghost text-slate-400 hover:text-blue-600" title="ویرایش">
                                            <Edit size={14}/>
                                        </Link>
                                    </div>
                                </div>
                            ))}
                            
                            {/* دکمه افزودن زیردسته جدید */}
                            <div className="mt-3 pr-7">
                                <Link to={`edit/${category.id}`} className="text-xs text-primary hover:underline flex items-center gap-1 opacity-70 hover:opacity-100">
                                    <Box size={12}/> مدیریت زیرمجموعه‌ها
                                </Link>
                            </div>
                        </div>
                    </motion.div>
                </td>
            </tr>
        )}
      </AnimatePresence>
    </>
  );
};

export default CategoryRow;