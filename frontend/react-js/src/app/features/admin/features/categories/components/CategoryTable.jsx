// src/app/features/admin/categories/components/CategoryTable.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Edit, Trash2, Eye, CheckCircle2, XCircle, 
  ArrowUp, ArrowDown, CornerDownRight, Layers, Image as ImageIcon
} from 'lucide-react';
import clsx from 'clsx';

const CategoryTable = ({ 
  categories, 
  selectedIds, 
  onSelectAll, 
  onSelectOne, 
  onDelete, 
  onToggleStatus, 
  sortConfig, 
  onSort,
  viewMode
}) => {
  
  const ThSortable = ({ label, sortKey, className }) => (
    <th 
      onClick={() => onSort && onSort(sortKey)}
      className={clsx("cursor-pointer hover:bg-base-200 transition-colors select-none py-4", className)}
    >
      <div className="flex items-center gap-2 text-slate-600">
        {label}
        {sortConfig?.key === sortKey && (
          sortConfig.direction === 'asc' 
            ? <ArrowUp size={14} className="text-primary"/> 
            : <ArrowDown size={14} className="text-primary"/>
        )}
      </div>
    </th>
  );

  return (
    <div className="bg-white rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 overflow-hidden relative min-h-[500px]">
      <div className="overflow-x-auto">
        <table className="table w-full">
          <thead className="bg-slate-50/80 text-xs uppercase font-bold tracking-wider border-b border-slate-100 backdrop-blur-md sticky top-0 z-10">
            <tr>
              <th className="w-16 text-center">
                <label>
                  <input 
                      type="checkbox" 
                      className="checkbox checkbox-sm checkbox-primary rounded-md"
                      checked={categories.length > 0 && selectedIds.length === categories.length}
                      onChange={onSelectAll}
                  />
                </label>
              </th>
              <th className="w-20 text-right">تصویر</th>
              <ThSortable label="نام دسته‌بندی (ساختار درختی)" sortKey="name" />
              <ThSortable label="نامک (Slug)" sortKey="slug" />
              <ThSortable label="وضعیت" sortKey="is_active" className="text-center" />
              <th className="text-left pl-6 w-40">عملیات</th>
            </tr>
          </thead>
          
          <tbody className="divide-y divide-slate-50">
            {categories.length === 0 ? (
                <tr>
                    <td colSpan="6" className="text-center py-24 text-slate-400">
                        <div className="flex flex-col items-center gap-4 opacity-60">
                            <Layers size={64} strokeWidth={1}/>
                            <span className="text-lg">موردی یافت نشد!</span>
                        </div>
                    </td>
                </tr>
            ) : (
                categories.map((cat) => {
                  // محاسبه میزان تورفتگی برای حالت درختی
                  const indentLevel = viewMode === 'tree' ? (cat.level || 0) : 0;
                  const paddingRight = indentLevel * 30; // هر سطح 30 پیکسل فاصله

                  return (
                    <tr 
                        key={cat.id} 
                        className={clsx(
                            "group hover:bg-blue-50/30 transition-colors duration-200 text-right",
                            selectedIds.includes(cat.id) && "bg-blue-50/60"
                        )}
                    >
                      {/* Checkbox */}
                      <th className="text-center">
                        <label>
                          <input 
                            type="checkbox" 
                            className="checkbox checkbox-sm checkbox-primary rounded-md"
                            checked={selectedIds.includes(cat.id)}
                            onChange={() => onSelectOne(cat.id)}
                          />
                        </label>
                      </th>

                      {/* Image */}
                      <td>
                        <Link to={`/admin/categories/${cat.id}`}>
                            <div className="avatar">
                                <div className="w-12 h-12 rounded-xl ring-1 ring-slate-100 bg-white p-0.5">
                                    {cat.banner_box ? (
                                        <img src={cat.banner_box} alt={cat.name} className="object-cover rounded-lg" />
                                    ) : (
                                        <div className="w-full h-full bg-slate-50 flex items-center justify-center text-slate-300 rounded-lg">
                                            <ImageIcon size={20}/>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </Link>
                      </td>

                      {/* Name (Tree View Logic) */}
                      <td style={{ paddingRight: viewMode === 'tree' ? `${paddingRight + 16}px` : undefined }}>
                        <div className="flex items-center gap-2">
                            {viewMode === 'tree' && indentLevel > 0 && (
                                <CornerDownRight size={16} className="text-slate-300" strokeWidth={2} />
                            )}
                            <Link to={`edit/${cat.id}`} className="font-bold text-slate-700 hover:text-primary transition-colors text-sm">
                                {cat.name}
                            </Link>
                            {/* نشانگر والد/فرزند */}
                            {(!cat.parent && viewMode === 'tree') && <span className="badge badge-ghost badge-xs text-[9px]">ریشه</span>}
                        </div>
                      </td>

                      {/* Slug */}
                      <td>
                        <div className="font-mono text-xs text-slate-400 dir-ltr text-right truncate max-w-[150px]">
                            /{cat.slug}
                        </div>
                      </td>

                      {/* Status */}
                      <td className="text-center">
                        <button 
                            onClick={() => onToggleStatus([cat.id], !cat.is_active)}
                            className={clsx(
                                "badge gap-1 py-3 px-3 border-0 transition-all cursor-pointer font-medium text-xs",
                                cat.is_active 
                                    ? "bg-emerald-50 text-emerald-600 hover:bg-emerald-100" 
                                    : "bg-red-50 text-red-600 hover:bg-red-100"
                            )}
                        >
                            {cat.is_active ? 'فعال' : 'غیرفعال'}
                        </button>
                      </td>

                      {/* Actions */}
                      <td>
                        <div className="flex justify-end items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                            <Link 
                                to={`/admin/categories/${cat.id}`}
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-primary tooltip tooltip-top"
                                data-tip="مشاهده"
                            >
                                <Eye size={16} />
                            </Link>
                            
                            <Link 
                                to={`edit/${cat.id}`}
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-blue-600 tooltip tooltip-top"
                                data-tip="ویرایش"
                            >
                                <Edit size={16} />
                            </Link>

                            <button 
                                onClick={() => onDelete(cat.id)}
                                className="btn btn-sm btn-ghost btn-square text-slate-400 hover:text-red-500 tooltip tooltip-top"
                                data-tip="حذف"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CategoryTable;