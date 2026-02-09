// src/app/features/admin/categories/components/CategoryRow.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Edit, Trash2, Eye, CheckCircle2, XCircle, 
  ChevronDown, ChevronLeft, CornerDownRight, ImageIcon 
} from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';
import { adminCategoryService } from '../../../services/adminCategoryService';

const CategoryRow = ({ 
  category, 
  isSelected, 
  onSelect, 
  onDelete, 
  onToggleStatus 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = category.children_count > 0;

  // Lazy Fetch Children (فقط وقتی باز می‌شود درخواست می‌زند)
  const { data: details, isLoading: isLoadingChildren } = useQuery({
    queryKey: ['category-details', category.id],
    queryFn: () => adminCategoryService.getById(category.id),
    enabled: isExpanded && hasChildren, // شرط اجرای کوئری
    staleTime: 1000 * 60 * 5,
  });

  const subCategories = details?.children || [];

  return (
    <>
      {/* --- سطر والد --- */}
      <tr className={clsx("group hover:bg-slate-50 transition-colors border-b border-slate-50", isSelected && "bg-blue-50/50")}>
        {/* Checkbox */}
        <th className="text-center">
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
        <td>
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
            {hasChildren ? (
                <button 
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="btn btn-xs btn-circle btn-ghost text-slate-400 hover:bg-slate-200 hover:text-slate-700 transition-all"
                >
                    {isExpanded ? <ChevronDown size={16}/> : <ChevronLeft size={16}/>}
                </button>
            ) : (
                <span className="w-6 h-6 inline-block"></span> // Spacer
            )}
            
            <div className="flex flex-col">
                <Link to={`edit/${category.id}`} className="font-bold text-slate-700 hover:text-primary transition-colors text-sm">
                    {category.name}
                </Link>
                {hasChildren && (
                    <span className="text-[10px] text-slate-400">{category.children_count} زیرمجموعه</span>
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
        <td className="text-center">
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
        <td>
          <div className="flex justify-end items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
            <Link to={`edit/${category.id}`} className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600">
                <Edit size={16} />
            </Link>
            <button onClick={() => onDelete(category.id)} className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500">
                <Trash2 size={16} />
            </button>
          </div>
        </td>
      </tr>

      {/* --- سطر آکاردئون (فرزندان) --- */}
      <AnimatePresence>
        {isExpanded && hasChildren && (
            <tr>
                <td colSpan="6" className="p-0 border-0">
                    <motion.div 
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="bg-slate-50/50 overflow-hidden shadow-inner"
                    >
                        <div className="pr-16 pl-4 py-4 space-y-2 relative border-r-4 border-primary/20 mr-8 my-2 rounded-l-xl">
                            {isLoadingChildren ? (
                                <div className="flex items-center gap-2 text-sm text-slate-400 py-2">
                                    <span className="loading loading-spinner loading-xs"></span> در حال دریافت زیرمجموعه‌ها...
                                </div>
                            ) : subCategories.length === 0 ? (
                                <div className="text-sm text-slate-400 italic">هیچ زیرمجموعه‌ای یافت نشد.</div>
                            ) : (
                                <table className="table table-sm w-full bg-transparent">
                                    <tbody>
                                        {subCategories.map(sub => (
                                            <tr key={sub.id} className="hover:bg-slate-100/50 border-b border-slate-100 last:border-0">
                                                <td className="w-8">
                                                    <CornerDownRight size={16} className="text-slate-300"/>
                                                </td>
                                                <td>
                                                    <Link to={`edit/${sub.id}`} className="font-medium text-slate-600 hover:text-primary text-sm flex items-center gap-2">
                                                        {sub.name}
                                                    </Link>
                                                </td>
                                                <td className="font-mono text-xs text-slate-400 dir-ltr text-right">
                                                    /{sub.slug || 'no-slug'}
                                                </td>
                                                <td className="text-left w-24">
                                                    <Link to={`edit/${sub.id}`} className="btn btn-xs btn-ghost text-slate-400 hover:text-blue-600">
                                                        <Edit size={14}/>
                                                    </Link>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                            <div className="mt-3 pt-2 border-t border-slate-200">
                                <Link to={`edit/${category.id}`} className="btn btn-xs btn-outline btn-primary gap-1">
                                    <Edit size={12}/> مدیریت زیرمجموعه‌ها
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