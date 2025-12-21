// src/app/features/admin/customers/components/CustomerRow.jsx
import { memo } from 'react';
import { MoreVertical, Edit, Trash2 } from 'lucide-react';
import { formatPrice } from '../../../utils/formatPrice';
import clsx from 'clsx';

const CustomerRow = memo(({ user, isSelected, onToggle, onEdit }) => {
  return (
    <tr className={clsx(
      "group transition-colors duration-200",
      isSelected ? "bg-primary/5" : "hover:bg-base-200/40"
    )}>
      {/* Checkbox */}
      <th>
        <label className="cursor-pointer p-2 -m-2 block">
          <input 
            type="checkbox" 
            className="checkbox checkbox-sm checkbox-primary rounded-md transition-all"
            checked={isSelected}
            onChange={() => onToggle(user.id)}
          />
        </label>
      </th>

      {/* User Info */}
      <td>
        <div className="flex items-center gap-3">
          <div className="avatar placeholder">
            <div className={clsx(
              "rounded-full w-10 h-10 ring-2 ring-offset-2 ring-offset-base-100 transition-all",
              user.is_active ? "bg-neutral text-neutral-content flex items-center justify-center ring-success/20" : "bg-base-300 text-base-content/50 ring-error/20"
            )}>
              <span className="text-sm font-bold uppercase">{user.username.slice(0, 2)}</span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-base-content leading-tight">
              {user.first_name || user.username} {user.last_name}
            </span>
            <span className="text-xs text-base-content/50 font-mono mt-0.5 dir-ltr text-right">
              {user.email}
            </span>
          </div>
        </div>
      </td>

      {/* Status */}
      <td>
        <div className={clsx(
          "badge gap-1.5 text-xs font-medium py-3 px-3 border-none",
          user.is_active 
            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400" 
            : "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400"
        )}>
          <span className={clsx("w-1.5 h-1.5 rounded-full", user.is_active ? "bg-emerald-500" : "bg-red-500")}></span>
          {user.is_active ? 'فعال' : 'مسدود'}
        </div>
      </td>

      {/* Role */}
      <td>
        <div className="flex flex-col gap-1">
            {user.is_superuser ? (
                <span className="badge badge-primary badge-outline text-xs">مدیر کل</span>
            ) : user.is_staff ? (
                <span className="badge badge-secondary badge-outline text-xs">کارمند</span>
            ) : (
                <span className="text-sm text-base-content/70">مشتری</span>
            )}
            {user.company && (
                <span className="text-[10px] text-base-content/40 truncate max-w-[100px]" title={user.company}>
                    {user.company}
                </span>
            )}
        </div>
      </td>

      {/* Wallet */}
      <td>
        <div className="font-mono font-medium text-sm flex items-center gap-1 dir-ltr">
            <span>{formatPrice(user.wallet_balance)}</span>
            <span className="text-[10px] text-base-content/50">IQD</span>
        </div>
      </td>

      {/* Created At */}
      <td className="text-xs text-base-content/60 font-mono">
        {new Date(user.created_at).toLocaleDateString('fa-IR')}
      </td>

      {/* Actions */}
      <td className="text-left">
        <button 
            onClick={() => onEdit(user)}
            className="btn btn-ghost btn-sm btn-square text-base-content/60 hover:text-primary hover:bg-primary/10 transition-colors"
            title="ویرایش"
        >
            <Edit size={16} />
        </button>
      </td>
    </tr>
  );
});

CustomerRow.displayName = 'CustomerRow';
export default CustomerRow;