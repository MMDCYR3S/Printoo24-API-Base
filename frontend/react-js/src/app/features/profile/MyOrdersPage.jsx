import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Package, Calendar, MapPin, ChevronLeft, AlertCircle } from 'lucide-react';
import { profileService } from '../../services/profileService';

import pageText from '../../lang/pages.json'
import globalText from '../../lang/global.json'

const getStatusColor = (status) => {
  if (!status) return 'badge-ghost';
  if (status.includes('تحویل') || status.includes('تکمیل')) return 'badge-success text-white shadow-success/20 shadow-lg';
  if (status.includes('چاپ') || status.includes('آماده')) return 'badge-warning text-white shadow-warning/20 shadow-lg';
  if (status.includes('لغو') || status.includes('رد')) return 'badge-error text-white shadow-error/20 shadow-lg';
  return 'badge-info text-white shadow-info/20 shadow-lg';
};

const MyOrdersPage = () => {
  const { data: rawData, isLoading } = useQuery({
    queryKey: ['profile-orders'],
    queryFn: profileService.getOrders,
  });

  // هندل کردن آرایه تو در تو [[{...}]]
  const orders = Array.isArray(rawData?.[0]) ? rawData[0] : (rawData || []);

  if (isLoading) return <div className="flex justify-center py-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center border-b border-slate-100 pb-4">
        <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
          <Package className="text-primary" /> {pageText.profile.myOrdersPage.myOrders}
        </h1>
        <div className="badge badge-lg badge-primary badge-outline font-bold">{orders.length} {pageText.profile.myOrdersPage.order}</div>
      </div>

      <div className="grid gap-4">
        {orders.length === 0 ? (
          <div className="text-center py-16 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
             <Package size={48} className="mx-auto text-slate-300 mb-4" />
             <p className="text-slate-500 font-bold">{pageText.profile.myOrdersPage.notRegisteredOrder}</p>
             <Link to="/shop" className="btn btn-primary btn-sm mt-4">{pageText.profile.myOrdersPage.registerFirstOrder}</Link>
          </div>
        ) : (
          orders.map((order) => (
            <div key={order.id} className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-all group relative overflow-hidden">
               {/* نوار رنگی وضعیت */}
               <div className={`absolute left-0 top-0 bottom-0 w-1 ${getStatusColor(order.status).replace('text-white', '').replace('badge-', 'bg-').split(' ')[0]}`}></div>
               
               <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4 pl-4">
                 <div className="flex gap-4 items-center">
                   <div className="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-400 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                      <span className="font-black text-lg">#{order.id}</span>
                   </div>
                   <div>
                     <h3 className="font-bold text-slate-800 text-lg">{order.type_display || pageText.profile.myOrdersPage.registerPrint}</h3>
                     <div className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                        <Calendar size={12}/> {new Date(order.created_at).toLocaleDateString('fa-IR')}
                     </div>
                   </div>
                 </div>
                 
                 <span className={`badge border-none px-4 py-3 h-auto font-bold text-xs ${getStatusColor(order.status)}`}>
                   {order.status}
                 </span>
               </div>
               
               <div className="flex flex-col md:flex-row items-start md:items-center justify-between pt-4 border-t border-slate-50 gap-4 pl-4">
                 <div className="flex items-center gap-2 text-xs font-medium text-slate-500 bg-slate-50 px-3 py-2 rounded-xl">
                   <MapPin size={14} className="text-slate-400"/> 
                   <span className="truncate max-w-[250px]">{order.address || pageText.profile.myOrdersPage.notRegisteredAddress}</span>
                 </div>
                 
                 <div className="flex items-center gap-4 w-full md:w-auto justify-between">
                   <div className="text-right">
                      <span className="block text-[10px] text-slate-400">{pageText.profile.myOrdersPage.totalPrice}</span>
                      <span className="font-black text-lg text-slate-700 dir-ltr">
                        {new Intl.NumberFormat('fa-IQ').format(order.total_price)} <span className="text-xs font-medium text-slate-400">{globalText.currency}</span>
                      </span>
                   </div>
                   <Link to={`/profile/orders/${order.id}`} className="btn btn-primary rounded-xl px-6 shadow-lg shadow-primary/20">
                     {pageText.profile.myOrdersPage.details} <ChevronLeft size={16} />
                   </Link>
                 </div>
               </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MyOrdersPage;