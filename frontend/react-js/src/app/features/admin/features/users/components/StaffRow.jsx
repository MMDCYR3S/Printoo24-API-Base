import { ShieldAlert, Edit2, Trash2, Mail, User, Clock } from 'lucide-react';

const StaffRow = ({ member, isSelected, onToggle, onEdit, onDelete }) => {
  // رنگ‌بندی برای نقش‌های مختلف جهت زیبایی بصری
  const roleColors = {
    admin: 'bg-red-50 text-red-700 border-red-100',
    designer: 'bg-blue-50 text-blue-700 border-blue-100',
    print: 'bg-purple-50 text-purple-700 border-purple-100',
    logistics: 'bg-orange-50 text-orange-700 border-orange-100',
    financial: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  };

  const roleStyle = roleColors[member.role?.slug] || 'bg-slate-50 text-slate-700 border-slate-100';

  return (
    <tr className={`hover:bg-slate-50/80 transition-colors ${isSelected ? 'bg-secondary/5' : ''}`}>
      <th className="w-12">
        <label className="cursor-pointer">
          <input 
            type="checkbox" 
            className="checkbox checkbox-sm checkbox-secondary rounded-md" 
            checked={isSelected}
            onChange={() => onToggle(member.id)}
          />
        </label>
      </th>
      
      <td>
        <div className="flex items-center gap-3">
          <div className={`avatar placeholder ${member.is_active ? 'online' : 'offline'}`}>
            <div className="bg-slate-100 text-slate-400 rounded-xl w-10">
              <User size={20} />
            </div>
          </div>
          <div>
            <div className="font-bold text-slate-800 flex items-center gap-2">
              {member.username}
              {member.is_superuser && (
                <div className="badge badge-warning badge-sm gap-1 py-2 font-black text-[10px]">
                  <ShieldAlert size={12} /> مدیر کل
                </div>
              )}
            </div>
            <div className="text-xs text-slate-500 flex items-center gap-1 mt-1 font-mono">
              <Mail size={12} /> {member.email}
            </div>
          </div>
        </div>
      </td>

      <td>
        <span className={`px-3 py-1 rounded-lg border text-xs font-bold ${roleStyle}`}>
          {member.role?.name || 'بدون نقش'}
        </span>
      </td>

      <td>
        {member.is_active ? (
          <span className="flex items-center gap-1.5 text-emerald-600 text-xs font-bold bg-emerald-50 px-2 py-1 rounded-full w-fit">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
            فعال
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-slate-400 text-xs font-bold bg-slate-50 px-2 py-1 rounded-full w-fit">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
            غیرفعال
          </span>
        )}
      </td>

      <td>
        <div className="text-xs text-slate-500 font-mono flex items-center gap-1">
          <Clock size={12} className="text-slate-400" />
          {new Date(member.created_at).toLocaleDateString('fa-IR')}
        </div>
      </td>

      <td className="text-left">
        <div className="flex justify-end gap-1">
          <button 
            onClick={() => onEdit(member)}
            className="btn btn-ghost btn-sm text-slate-500 hover:text-secondary tooltip" 
            data-tip="ویرایش دسترسی"
          >
            <Edit2 size={16} />
          </button>
          {!member.is_superuser && (
            <button 
              onClick={() => onDelete(member.id)}
              className="btn btn-ghost btn-sm text-slate-400 hover:text-error tooltip" 
              data-tip="حذف کارمند"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </td>
    </tr>
  );
};

export default StaffRow;