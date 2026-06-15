import React, { memo } from 'react';
import { Edit, Shield, ShieldAlert, Wallet, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CustomerRow = memo(({ user, isSelected, onToggle, onEdit, onWalletAction }) => {
  const navigate = useNavigate(); 

  // تابعی برای رفتن به صفحه دیتیل
  const handleRowClick = () => {
    navigate(`${user.id}`);
  };
  return (
    <tr className={`group transition-colors hover:bg-slate-50 ${isSelected ? 'bg-primary/5' : ''} `}>
      
      {/* 1. Checkbox */}
      <th>
        <label className="cursor-pointer">
          <input 
            type="checkbox" 
            className="checkbox checkbox-sm checkbox-primary rounded-md"
            checked={isSelected}
            onChange={() => onToggle(user.id)}
          />
        </label>
      </th>

      {/* 2. User Info */}
      <td>
        <div onClick={handleRowClick} className="flex items-center gap-3">

          <div>
          <div className="font-bold text-slate-700 text-sm flex items-center gap-1">
  {user.phone_number}
  {user.is_superuser && <ShieldAlert size={14} className="text-amber-500" />}
</div>
<div className="text-[11px] text-slate-400 font-mono">
  {user.first_name || user.last_name 
    ? `${user.first_name} ${user.last_name}`.trim() 
    : '---'}
</div>
          </div>
        </div>
      </td>

      {/* 3. Status */}
      <td>
        <div className={`badge badge-sm border-0 font-medium ${user.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
          {user.is_active ? 'فعال' : 'غیرفعال'}
        </div>
      </td>

      {/* 4. Role */}
      <td>
        {user.is_staff ? (
          <span className="flex items-center gap-1 text-xs font-bold text-purple-600 bg-purple-50 px-2 py-1 rounded-lg w-fit">
            <Shield size={12} /> کارمند
          </span>
        ) : (
          <span className="text-xs text-slate-500">کاربر عادی</span>
        )}
      </td>

      {/* 5. Wallet Balance (ستون جدید برای نمایش موجودی) */}
      <td className="text-right dir-ltr">
        <div className="flex flex-col items-end">
            <span className={`font-mono font-bold text-sm ${Number(user.wallet_balance) < 0 ? 'text-red-500' : 'text-slate-700'}`}>
                {new Intl.NumberFormat('en-US').format(user.wallet_balance || 0)}
            </span>
            <span className="text-[9px] text-slate-400 font-bold">IQD</span>
        </div>
      </td>

      {/* 6. Created At */}
      <td className="text-xs text-slate-500 font-mono">
        {new Date(user.created_at).toLocaleDateString('fa-IR')}
      </td>

      {/* 7. Actions (دکمه‌ها اینجان) */}
      <td>
        <div className="flex items-center gap-2">
          
          {/* دکمه اختصاصی کیف پول */}
          <button 
            onClick={(e) => { e.stopPropagation(); onWalletAction(user); }}
            className="btn btn-sm btn-square btn-ghost text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 tooltip tooltip-top"
            data-tip="مدیریت کیف پول"
          >
            <Wallet size={18} />
          </button>


                    <a href= {'users/' + user.id}
            // onClick={handleRowClick} 
            className="btn btn-sm btn-square btn-ghost text-blue-600 hover:bg-emerald-50 hover:text-emerald-700 tooltip tooltip-top"
            data-tip="جزئیات کاربر"
          >
            <Eye size={18} />
          </a>
{/* onClick={handleRowClick} */}
          {/* دکمه ویرایش */}
          <button 
            onClick={(e) => { e.stopPropagation(); onEdit(user); }}
            className="btn btn-sm btn-square btn-ghost text-slate-600 hover:bg-blue-50 hover:text-blue-700 tooltip tooltip-top"
            data-tip="ویرایش کاربر"
          >
            <Edit size={18} />
          </button>

        </div>
      </td>
    </tr>
  );
});

export default CustomerRow;