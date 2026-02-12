// src/app/features/admin/customers/components/CustomerRow.jsx
import React, { memo } from 'react';
import { MoreHorizontal, Edit, Trash2, Shield, ShieldAlert, Wallet } from 'lucide-react';

const CustomerRow = memo(({ user, isSelected, onToggle, onEdit, onWalletAction }) => {
  return (
    <tr className={`hover:bg-slate-50/80 transition-colors group ${isSelected ? 'bg-primary/5' : ''}`}>
      
      {/* Checkbox */}
      <th>
        <label>
          <input 
            type="checkbox" 
            className="checkbox checkbox-sm checkbox-primary rounded-md"
            checked={isSelected}
            onChange={() => onToggle(user.id)}
          />
        </label>
      </th>

      {/* User Info */}
      <td>
        <div className="flex items-center gap-3">
          <div className="avatar placeholder">
            <div className="bg-neutral text-neutral-content rounded-full w-10 ring-1 ring-slate-100">
              <span className="text-xs font-bold uppercase">{user.username?.substring(0, 2)}</span>
            </div>
          </div>
          <div>
            <div className="font-bold text-slate-700 text-sm flex items-center gap-1">
              {user.username}
              {user.is_superuser && <ShieldAlert size={12} className="text-warning" />}
            </div>
            <div className="text-[11px] text-slate-400 font-mono">{user.email || 'No Email'}</div>
          </div>
        </div>
      </td>

      {/* Status */}
      <td>
        <div className={`badge badge-sm gap-1 font-medium border-0 ${user.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${user.is_active ? 'bg-emerald-500' : 'bg-slate-400'}`}></div>
          {user.is_active ? 'فعال' : 'غیرفعال'}
        </div>
      </td>

      {/* Role */}
      <td>
        {user.is_staff ? (
          <span className="flex items-center gap-1 text-xs font-bold text-purple-600 bg-purple-50 px-2 py-1 rounded-lg w-fit">
            <Shield size={12} /> کارمند
          </span>
        ) : (
          <span className="text-xs text-slate-500">کاربر عادی</span>
        )}
      </td>

      {/* Wallet Balance (نمایش ساده) */}
      <td className="font-mono text-sm dir-ltr text-right">
        <span className={Number(user.wallet_balance) < 0 ? 'text-red-500' : 'text-slate-600'}>
          {new Intl.NumberFormat('en-US').format(user.wallet_balance || 0)}
        </span>
        <span className="text-[10px] text-slate-400 ml-1">IQD</span>
      </td>

      {/* Created At */}
      <td className="text-xs text-slate-500 font-mono">
        {new Date(user.created_at).toLocaleDateString('fa-IR')}
      </td>

      {/* Actions */}
      <td>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          
          {/* دکمه کیف پول */}
          <button 
            onClick={() => onWalletAction(user)}
            className="btn btn-ghost btn-xs btn-square text-emerald-600 hover:bg-emerald-50 tooltip tooltip-top"
            data-tip="مدیریت کیف پول"
          >
            <Wallet size={16} />
          </button>

          <button 
            onClick={() => onEdit(user)}
            className="btn btn-ghost btn-xs btn-square text-blue-600 hover:bg-blue-50 tooltip tooltip-top"
            data-tip="ویرایش"
          >
            <Edit size={16} />
          </button>
        </div>
      </td>
    </tr>
  );
});

export default CustomerRow;