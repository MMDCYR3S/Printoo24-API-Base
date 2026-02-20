import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { 
  User, Wallet, Package, MapPin, Edit2, Check, X, 
  TrendingUp, Clock, AlertCircle 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { profileService } from '../../services/profileService';

// فایل ترجمه
import pageText from '../../lang/pages.json'
import globalText from '../../lang/global.json'


const ProfileDashboard = () => {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  // 1. دریافت اطلاعات پروفایل
  const { data: user, isLoading: isUserLoading } = useQuery({
    queryKey: ['profile-info'],
    queryFn: profileService.getProfileInfo,
  });

  // 2. دریافت موجودی کیف پول
  const { data: wallet, isLoading: isWalletLoading } = useQuery({
    queryKey: ['wallet-balance'],
    queryFn: profileService.getWalletBalance,
  });

  // فرمت کردن عدد پول
  const formattedBalance = wallet?.decimal 
    ? new Intl.NumberFormat('fa-IQ').format(Number(wallet.decimal)) 
    : '0';

  // 3. تنظیمات فرم ادیت
  const { register, handleSubmit, reset, setValue } = useForm();

  // وقتی دیتا آمد، فرم را پر کن
  useEffect(() => {
    if (user) {
      setValue('first_name', user.first_name);
      setValue('last_name', user.last_name);
      setValue('company', user.company);
      setValue('phone_number', user.phone_number);
    }
  }, [user, setValue]);

  // 4. Mutation برای آپدیت پروفایل
  const updateMutation = useMutation({
    mutationFn: profileService.updateProfileInfo,
    onSuccess: () => {
      toast.success(pageText.profile.infoUpdateSuccess);
      setIsEditing(false);
      queryClient.invalidateQueries(['profile-info']); // رفرش دیتا
    },
    onError: () => {
      toast.error(pageText.profile.infoUpdateError);
    }
  });

  const onSubmit = (data) => {
    updateMutation.mutate(data);
  };

const { data: orders } = useQuery({
    queryKey: ['profile-orders'],
    queryFn: profileService.getOrders,
  });

  const { data: addresses } = useQuery({
    queryKey: ['profile-addresses'],
    queryFn: profileService.getAddresses,
  });

  // فلت کردن دیتا برای گرفتن تعداد صحیح (چون API آرایه تو در تو برمی‌گرداند)
  const ordersList = Array.isArray(orders?.[0]) ? orders[0] : (orders || []);
  const activeOrdersCount = ordersList.filter(o => o.status !== pageText.profile.delivered && o.status !== pageText.profile.cancelled).length;
  
  const addressesList = Array.isArray(addresses?.[0]) ? addresses[0] : (addresses || []);
  const addressCount = addressesList.length;



  const handleWalletClick = () => {
    window.open('https://wa.me/9647700805867', '_blank');
  };

  if (isUserLoading || isWalletLoading) {
    return <DashboardSkeleton />;
  }

  return (
    <div className=" p-4 md:p-12 space-y-6 pb-20 lg:pb-0 animate-in fade-in duration-500">
      
      {/* ردیف بالا: اطلاعات کاربر + کیف پول */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* === کارت اطلاعات کاربری (Editable) === */}
        <div className="xl:col-span-2 bg-gray-100 rounded-3xl p-6 shadow-sm border border-slate-100 relative overflow-hidden">
          <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
            <h2 className="text-xl font-black text-slate-800 flex items-center gap-2">
              <User className="text-primary" />
              {pageText.profile.profileInfo}
            </h2>
            <button 
              onClick={() => {
                if(isEditing) reset(); // اگر کنسل کرد برگرده به حالت قبل
                setIsEditing(!isEditing);
              }}
              className={`btn btn-sm btn-ghost gap-2 ${isEditing ? 'text-error' : 'text-slate-400'}`}
            >
              {isEditing ? <><X size={16}/> {globalText.buttons.cancel}</> : <><Edit2 size={16}/> {globalText.buttons.edit}</>}
            </button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* فیلدهای غیر قابل ویرایش */}
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-400">{pageText.profile.username}</label>
                <input type="text" value={user?.username} disabled className="input input-bordered  bg-white text-slate-400" />
              </div>
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-400">{pageText.profile.email}</label>
                <input type="text" value={user?.email} disabled className="input input-bordered  bg-white text-slate-400 dir-ltr text-right" />
              </div>

              {/* فیلدهای قابل ویرایش */}
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-500 font-bold">{pageText.profile.firstName}</label>
                <br/>
                <input 
                  type="text" 
                  disabled={!isEditing}
                  className={`input input-bordered ${isEditing ? 'bg-gray-100 border-primary' : ' bg-white border-transparent'}`}
                  {...register('first_name')}
                />
              </div>
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-500 font-bold">{pageText.profile.lastName}</label>
                <br/>
                <input 
                  type="text" 
                  disabled={!isEditing}
                  className={`input input-bordered ${isEditing ? 'bg-gray-100 border-primary' : ' bg-white border-transparent'}`}
                  {...register('last_name')}
                />
              </div>
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-500 font-bold">{pageText.profile.companyName}</label>
                <br/>
                <input 
                  type="text" 
                  disabled={!isEditing}
                  className={`input input-bordered ${isEditing ? 'bg-gray-100 border-primary' : ' bg-white border-transparent'}`}
                  {...register('company')}
                />
              </div>
              <div className="form-control">
                <label className="label mx-2  text-xs text-slate-500 font-bold">{pageText.profile.phoneNumber}</label>
                <br/>
                <input 
                  type="text" 
                  disabled={!isEditing}
                  dir="ltr"
                  className={`input input-bordered text-right ${isEditing ? 'bg-gray-100 border-primary' : ' bg-white border-transparent'}`}
                  {...register('phone_number')}
                />
              </div>
            </div>

            {/* دکمه ذخیره - فقط در حالت ادیت */}
            {isEditing && (
              <div className="mt-6 flex justify-end animate-in slide-in-from-bottom-2">
                <button 
                  type="submit" 
                  disabled={updateMutation.isPending}
                  className="btn btn-primary px-8 shadow-lg shadow-primary/20"
                >
                  {updateMutation.isPending ? <span className="loading loading-spinner"></span> : <><Check size={18} /> {pageText.profile.saveChanges}</>}
                </button>
              </div>
            )}
          </form>
        </div>

        {/* === کارت کیف پول (Wallet) === */}
        <div 
          onClick={handleWalletClick}
          className="xl:col-span-1 bg-gradient-to-br from-slate-800 to-slate-900 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden group cursor-pointer tooltip tooltip-bottom w-full"
          data-tip={pageText.profile.clickToCharge}
        >
           {/* پترن پس‌زمینه */}
           <div className="absolute top-0 right-0 w-40 h-40 bg-gray-100/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 group-hover:bg-gray-100/10 transition-colors"></div>
           <div className="absolute bottom-0 left-0 w-32 h-32 bg-primary/20 rounded-full blur-3xl translate-y-1/2 -translate-x-1/3"></div>
           
           <div className="relative z-10 flex flex-col h-full justify-between min-h-[250px]">
             <div className="flex justify-between items-start">
               <div className="p-3 bg-gray-100/10 backdrop-blur-md rounded-2xl border border-white/5">
                 <Wallet size={28} className="text-emerald-400" />
               </div>
               <span className="bg-emerald-500/20 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/20">
                 {pageText.profile.active}
               </span>
             </div>
             
             <div className="space-y-1 text-center py-4">
               <span className="text-slate-400 text-sm font-medium block">{pageText.profile.walletAmount}</span>
               <div className="text-4xl font-black tracking-tight text-white drop-shadow-lg flex items-center justify-center gap-2 dir-ltr">
                 {formattedBalance}
                 <span className="text-lg opacity-60 font-medium">{globalText.currency}</span>
               </div>
             </div>
             
             <button className="w-full py-3 bg-gray-100/10 hover:bg-gray-100/20 active:scale-95 transition-all rounded-xl font-bold flex items-center justify-center gap-2 backdrop-blur-sm border border-white/5 group-hover:border-white/20">
               <TrendingUp size={18} />
               {pageText.profile.depositAmount}
             </button>
           </div>
        </div>
      </div>

      {/* ردیف پایین: دسترسی‌های سریع (Placeholders for future pages) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
{/* لینک سفارشات داینامیک */}
        <Link to="/profile/orders" className="bg-white p-6 rounded-3xl border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all group">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Package size={24} />
            </div>
            <div>
              <h3 className="font-bold text-slate-700">{pageText.profile.myOrders}</h3>
              <span className="text-xs text-slate-400">{pageText.profile.trackingOrder}</span>
            </div>
          </div>
          <div className="text-sm text-slate-500 flex justify-between items-center bg-slate-50 p-3 rounded-xl">
             <span>{pageText.profile.activeOrders}</span>
             <span className="font-bold text-slate-800">{activeOrdersCount} {pageText.profile.count}</span>
          </div>
        </Link>

        {/* لینک آدرس‌ها داینامیک */}
        <Link to="/profile/addresses" className="bg-white p-6 rounded-3xl border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all group">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-orange-50 text-orange-600 rounded-2xl group-hover:bg-orange-600 group-hover:text-white transition-colors">
              <MapPin size={24} />
            </div>
            <div>
              <h3 className="font-bold text-slate-700">{pageText.profile.addressManagement}</h3>
              <span className="text-xs text-slate-400">{pageText.profile.orderAddresses}</span>
            </div>
          </div>
          <div className="text-sm text-slate-500 flex justify-between items-center bg-slate-50 p-3 rounded-xl">
             <span>{pageText.profile.registeredAddress}</span>
             <span className="font-bold text-slate-800">{addressCount} {pageText.profile.item}</span>
          </div>
        </Link>

        {/* لینک  هزینه ها داینامیک */}
        <Link to="/profile/wallet" className="bg-white p-6 rounded-3xl border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all group">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-green-50 text-green-600 rounded-2xl group-hover:bg-green-600 group-hover:text-white transition-colors">
                               <Wallet size={24} className="" />
            </div>
            <div>
              <h3 className="font-bold text-slate-700">{pageText.profile.financeHistory}</h3>
              <span className="text-xs text-slate-400">{pageText.profile.yourFinancialHistory}</span>
            </div>
          </div>

        </Link>

      </div>

    </div>
  );
};

// اسکلتون لودینگ برای زیبایی UX
const DashboardSkeleton = () => (
  <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 animate-pulse">
    <div className="xl:col-span-2 bg-gray-100 h-[400px] rounded-3xl p-6"></div>
    <div className="xl:col-span-1 bg-slate-200 h-[400px] rounded-3xl"></div>
  </div>
);

export default ProfileDashboard;