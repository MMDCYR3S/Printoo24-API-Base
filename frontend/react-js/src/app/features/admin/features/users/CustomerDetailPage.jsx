import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCustomers } from './hooks/useCustomers';
import { 
  ArrowRight, User, Mail, Phone, MapPin, Calendar, 
  Wallet, Edit, Trash2, Shield, Building, FileText 
} from 'lucide-react';
import CustomerModal from './components/CustomerModal';
import WalletAdjustModal from '../../components/WalletAdjustModal';

const CustomerDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { useCustomer, deleteMutation } = useCustomers();
  
  // Fetch Data
  const { data: user, isLoading, isError } = useCustomer(id);

  // Modal States
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);

  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (isError || !user) return <div className="p-10 text-center text-slate-500">کاربر یافت نشد.</div>;

  const handleDelete = () => {
    if (window.confirm('آیا از حذف کامل این کاربر اطمینان دارید؟ این عملیات غیرقابل بازگشت است.')) {
      deleteMutation.mutate(user.id);
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8 pb-24">
      
      {/* --- Header --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="btn btn-circle btn-ghost btn-sm">
            <ArrowRight size={20}/>
          </button>
          <div>
            <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
              {user.first_name || user.last_name ? `${user.first_name} ${user.last_name}` : user.username}
              {user.is_superuser && <span className="badge badge-warning text-xs">مدیر کل</span>}
            </h1>
            <p className="text-slate-500 text-sm font-mono mt-1">ID: {user.id} • Join Date: {new Date(user.created_at).toLocaleDateString('EN')}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
           <button 
             onClick={() => setIsEditModalOpen(true)}
             className="btn btn-primary btn-outline gap-2 rounded-xl"
           >
             <Edit size={18} /> ویرایش پروفایل
           </button>
           <button 
             onClick={handleDelete}
             className="btn btn-error btn-ghost gap-2 rounded-xl text-red-500 hover:bg-red-50"
           >
             <Trash2 size={18} /> حذف کاربر
           </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* --- Col 1: Main Info --- */}
        <div className="lg:col-span-2 space-y-6">
            
            {/* Identity Card */}
            <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 relative overflow-hidden">
                <div className={`absolute top-0 right-0 w-full h-2 ${user.is_active ? 'bg-emerald-500' : 'bg-slate-300'}`}></div>
                
                <div className="flex flex-col sm:flex-row gap-6">

                    
                    <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 font-bold flex items-center gap-1"><User size={12}/> نام کاربری</label>
                            <div className="font-bold text-slate-700">{user.username}</div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 font-bold flex items-center gap-1"><Mail size={12}/> ایمیل</label>
                            <div className="font-mono text-sm text-slate-600">{user.email || '-'}</div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 font-bold flex items-center gap-1"><Phone size={12}/> موبایل</label>
                            <div className="font-mono text-sm text-slate-600">{user.phone_number || '-'}</div>
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs text-slate-400 font-bold flex items-center gap-1"><Building size={12}/> شرکت</label>
                            <div className="text-sm text-slate-600">{user.company || '-'}</div>
                        </div>
                         <div className="col-span-full space-y-1">
                            <label className="text-xs text-slate-400 font-bold flex items-center gap-1"><FileText size={12}/> بیوگرافی</label>
                            <p className="text-sm text-slate-500 leading-relaxed">{user.bio || 'توضیحاتی ثبت نشده است.'}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Address List */}
            <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
                <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <MapPin size={20} className="text-primary"/> آدرس‌ها
                </h3>
                
                {(!user.addresses || user.addresses.length === 0) ? (
                    <div className="text-center py-8 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <span className="text-slate-400 text-sm">هیچ آدرسی ثبت نشده است</span>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {user.addresses.map((addr, idx) => (
                            <div key={addr.id || idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-100 flex items-start gap-3 hover:bg-slate-100 transition-colors">
                                <div className="mt-1 min-w-[24px] h-6 flex items-center justify-center bg-white rounded-full text-xs font-bold text-slate-400 shadow-sm">
                                    {idx + 1}
                                </div>
                                <div>
                                    <div className="text-sm font-bold text-slate-700">
                                        {addr.province_name}، {addr.city_name}
                                    </div>
                                    <p className="text-xs text-slate-500 mt-1 leading-5">
                                        {addr.address}
                                    </p>
                                    <div className="mt-2 text-[10px] font-mono bg-white px-2 py-0.5 rounded border border-slate-200 w-fit text-slate-400">
                                        {addr.postal_code}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>

        {/* --- Col 2: Sidebar (Wallet & Status) --- */}
        <div className="space-y-6">
            
            {/* Wallet Card */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-3xl p-6 text-white shadow-xl shadow-slate-900/20 relative overflow-hidden">
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
                
                <div className="flex items-center gap-2 mb-6 opacity-80">
                    <Wallet size={20} />
                    <span className="text-sm font-bold">کیف پول</span>
                </div>

                <div className="mb-8">
                    <div className="text-4xl font-black font-mono tracking-tighter">
                        {Number(user.wallet_balance || 0).toLocaleString()}
                    </div>
                    <div className="text-sm opacity-50 font-bold mt-1">IQD (دینار عراق)</div>
                </div>

                <button 
                    onClick={() => setIsWalletModalOpen(true)}
                    className="btn btn-block bg-white/10 hover:bg-white/20 border-0 text-white backdrop-blur-md rounded-xl"
                >
                    مدیریت موجودی
                </button>
            </div>

            {/* Status & Access */}
            <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 space-y-4">
                <h3 className="font-bold text-slate-800 text-sm">وضعیت و دسترسی</h3>
                
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                    <span className="text-xs font-bold text-slate-500">وضعیت حساب</span>
                    {user.is_active ? (
                        <span className="badge badge-success badge-sm gap-1 text-white">
                             فعال
                        </span>
                    ) : (
                        <span className="badge badge-error badge-sm gap-1 text-white">
                             غیرفعال
                        </span>
                    )}
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                    <span className="text-xs font-bold text-slate-500">نقش کاربری</span>
                    {user.is_staff ? (
                        <span className="flex items-center gap-1 text-xs font-bold text-purple-600">
                            <Shield size={12}/> کارمند (Staff)
                        </span>
                    ) : (
                        <span className="text-xs text-slate-400">کاربر عادی</span>
                    )}
                </div>

                 <div className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                    <span className="text-xs font-bold text-slate-500">تاریخ عضویت</span>
                    <span className="text-xs font-mono text-slate-600">
                        {new Date(user.created_at).toLocaleDateString('EN')}
                    </span>
                </div>
            </div>

        </div>

      </div>

      {/* Modals */}
      {isEditModalOpen && (
        <CustomerModal 
            isOpen={isEditModalOpen} 
            onClose={() => setIsEditModalOpen(false)} 
            initialData={user}
        />
      )}

      {isWalletModalOpen && (
        <WalletAdjustModal
            isOpen={isWalletModalOpen}
            onClose={() => setIsWalletModalOpen(false)}
            user={user}
        />
      )}

    </div>
  );
};

export default CustomerDetailPage;