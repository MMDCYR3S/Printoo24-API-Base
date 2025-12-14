import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Package, Search, Calendar, MapPin } from 'lucide-react';
import { profileService } from '../../services/profileService';

const MyOrdersPage = () => {
  const { data: rawData, isLoading } = useQuery({
    queryKey: ['profile-orders'],
    queryFn: profileService.getOrders,
  });

  const orders = Array.isArray(rawData?.[0]) ? rawData[0] : (rawData || []);

  if (isLoading) return <div className="text-center py-10"><span className="loading loading-spinner text-primary"></span></div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-black text-slate-800">سفارش‌های من</h1>
        <div className="badge badge-primary badge-outline font-bold">{orders.length} سفارش</div>
      </div>

      <div className="grid gap-4">
        {orders.map((order) => (
          <div key={order.id} className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all group">
             <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
               <div className="flex gap-4">
                 <div className="w-14 h-14 bg-slate-100 rounded-xl flex items-center justify-center text-slate-400">
                    <Package size={24} />
                 </div>
                 <div>
                   <h3 className="font-bold text-slate-800 text-lg">{order.type_display}</h3>
                   <span className="text-xs text-slate-400 font-mono dir-ltr">ID: #{order.id}</span>
                 </div>
               </div>
               <span className={`badge font-bold p-3 text-xs ${order.status === 'در حال چاپ' ? 'badge-warning' : 'badge-ghost'}`}>
                 {order.status}
               </span>
             </div>
             
             <div className="flex flex-col md:flex-row items-start md:items-center justify-between pt-4 border-t border-slate-50 gap-3">
               <div className="flex flex-col gap-1 text-xs font-medium text-slate-500">
                 <div className="flex items-center gap-1"><Calendar size={14}/> {new Date(order.created_at).toLocaleDateString('fa-IR')}</div>
                 <div className="flex items-center gap-1"><MapPin size={14}/> <span className="truncate max-w-[200px]">{order.address}</span></div>
               </div>
               
               <div className="flex items-center gap-4 w-full md:w-auto justify-between">
                 <span className="font-black text-lg text-slate-700 dir-ltr">{new Intl.NumberFormat('fa-IQ').format(order.total_price)} <span className="text-xs font-medium text-slate-400">IQD</span></span>
                 <Link to={`/profile/orders/${order.id}`} className="btn btn-sm btn-primary btn-outline rounded-lg">
                   جزئیات سفارش
                 </Link>
               </div>
             </div>
          </div>
        ))}
        {orders.length === 0 && <p className="text-center text-slate-400 py-10">هنوز سفارشی ثبت نکرده‌اید.</p>}
      </div>
    </div>
  );
};

export default MyOrdersPage;