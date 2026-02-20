import { useState, useEffect } from 'react';
import { useAdminStaff } from '../hooks/useAdminStaff';
import { X, Shield, Mail, User, Lock, Save } from 'lucide-react';

const StaffModal = ({ isOpen, onClose, initialData = null }) => {
  const isEdit = !!initialData;
  const { rolesQuery, createMutation, updateMutation } = useAdminStaff();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role_id: '',
    is_active: true
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        username: initialData.username || '',
        email: initialData.email || '',
        role_id: initialData.role?.id || '',
        is_active: initialData.is_active ?? true,
        password: '' // در ادیت نیازی نیست
      });
    }
  }, [initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (isEdit) {
      // طبق API برای پچ فقط این دو مورد ارسال می‌شه
      updateMutation.mutate({
        id: initialData.id,
        data: { role_id: Number(formData.role_id), is_active: formData.is_active }
      }, { onSuccess: onClose });
    } else {
      createMutation.mutate({
        ...formData,
        role_id: Number(formData.role_id)
      }, { onSuccess: onClose });
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden border border-slate-100">
        <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-800 font-black">
            <div className="p-2 bg-secondary/10 text-secondary rounded-lg">
              <Shield size={20} />
            </div>
            {isEdit ? 'ویرایش دسترسی کارمند' : 'تعریف کارمند جدید'}
          </div>
          <button onClick={onClose} className="btn btn-ghost btn-sm btn-circle"><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="label text-xs font-bold text-slate-500">نام کاربری</label>
            <div className="relative">
              <User className="absolute right-3 top-3 text-slate-400" size={18} />
              <input 
                type="text"
                disabled={isEdit}
                className={`input input-bordered w-full pr-10 focus:input-secondary ${isEdit ? 'bg-slate-100 text-slate-400' : ''}`}
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
              />
            </div>
          </div>

          {!isEdit && (
            <>
              <div>
                <label className="label text-xs font-bold text-slate-500">ایمیل سازمانی</label>
                <div className="relative">
                  <Mail className="absolute right-3 top-3 text-slate-400" size={18} />
                  <input 
                    type="email"
                    className="input input-bordered w-full pr-10 focus:input-secondary"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="label text-xs font-bold text-slate-500">رمز عبور موقت</label>
                <div className="relative">
                  <Lock className="absolute right-3 top-3 text-slate-400" size={18} />
                  <input 
                    type="password"
                    className="input input-bordered w-full pr-10 focus:input-secondary"
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    required
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="label text-xs font-bold text-slate-500">نقش سازمانی</label>
            <select 
              className="select select-bordered w-full focus:select-secondary font-medium"
              value={formData.role_id}
              onChange={(e) => setFormData({...formData, role_id: e.target.value})}
              required
            >
              <option value="" disabled>انتخاب نقش...</option>
              {rolesQuery.data?.map(role => (
                <option key={role.id} value={role.id}>{role.name}</option>
              ))}
            </select>
          </div>

          {isEdit && (
            <div className="form-control bg-slate-50 p-3 rounded-xl border border-slate-100 mt-2">
              <label className="label cursor-pointer justify-between">
                <span className="label-text font-bold text-slate-700">وضعیت اکانت (فعال)</span> 
                <input 
                  type="checkbox" 
                  className="toggle toggle-secondary" 
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                />
              </label>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button 
              type="submit" 
              disabled={createMutation.isPending || updateMutation.isPending}
              className="btn btn-secondary flex-1 gap-2 shadow-lg shadow-secondary/20"
            >
              {(createMutation.isPending || updateMutation.isPending) ? (
                <span className="loading loading-spinner loading-sm"></span>
              ) : (
                <Save size={18} />
              )}
              {isEdit ? 'ذخیره تغییرات' : 'ایجاد اکانت'}
            </button>
            <button type="button" onClick={onClose} className="btn btn-ghost border-slate-200">انصراف</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StaffModal;