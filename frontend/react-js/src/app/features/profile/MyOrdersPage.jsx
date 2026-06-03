import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Package, Calendar, MapPin, ChevronLeft, Printer, FileCheck, ShoppingBag } from 'lucide-react';
import { profileService } from '../../services/profileService';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const STATUS_STYLES = {
  PENDING_REVIEW: { badge: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200/60',        dot: 'bg-blue-500',    card: 'bg-white' },
  DESIGNING:      { badge: 'bg-purple-50 text-purple-700 ring-1 ring-purple-200/60',  dot: 'bg-purple-500',  card: 'bg-white' },
  PRINTING:       { badge: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/60',     dot: 'bg-amber-500',   card: 'bg-white' },
  SHIPPED:        { badge: 'bg-sky-50 text-sky-700 ring-1 ring-sky-200/60',           dot: 'bg-sky-500',     card: 'bg-white' },
  DELIVERED:      { badge: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/60', dot: 'bg-emerald-500', card: 'bg-emerald-500/20' },
  CANCELED:       { badge: 'bg-red-50 text-red-600 ring-1 ring-red-200/60',           dot: 'bg-red-500',     card: 'bg-white' },
};

const getStatusStyle = (code) =>
  STATUS_STYLES[code] ?? { badge: 'bg-slate-100 text-slate-500', dot: 'bg-slate-400', card: 'bg-white' };

const MyOrdersPage = () => {
  const { data: rawData, isLoading } = useQuery({
    queryKey: ['profile-orders'],
    queryFn: profileService.getOrders,
  });

  const orders = Array.isArray(rawData?.[0]) ? rawData[0] : (rawData || []);

  if (isLoading) return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-5 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-slate-100 animate-pulse" />
          <div className="h-6 w-32 bg-slate-100 rounded-lg animate-pulse" />
        </div>
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-2xl ring-1 ring-black/[0.04] overflow-hidden">
          <div className="p-5 flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-slate-100 animate-pulse" />
            <div className="space-y-2 flex-1">
              <div className="h-4 w-40 bg-slate-100 rounded-lg animate-pulse" />
              <div className="h-3 w-24 bg-slate-50 rounded animate-pulse" />
            </div>
          </div>
          <div className="h-14 bg-slate-50/50 border-t border-slate-100/80 animate-pulse" />
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 max-w-[90vw] items-center mx-auto">
      {/* هدر */}
      <div className="flex justify-between items-center border-b border-slate-100 pb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Package size={19} className="text-primary" />
          </div>
          <h1 className="text-xl font-extrabold text-slate-800">
            {pageText.profile.myOrdersPage.myOrders}
          </h1>
        </div>
        <span className="text-xs font-bold text-primary bg-primary/8 px-3 py-1.5 rounded-full">
          {orders.length} {pageText.profile.myOrdersPage.order}
        </span>
      </div>

      <p className="text-slate-600">
        داواکارییەکەت لە ژێر پشکنینە. ئەگەر پەسەند بکرێت، لە ڕێگەی ژمارەی مۆبایلەکەتەوە ئاگادارت دەکەینەوە
      </p>

      <div className="space-y-3">
        {orders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 bg-white rounded-2xl ring-1 ring-black/[0.04]">
            <div className="w-20 h-20 rounded-3xl bg-slate-100 flex items-center justify-center mb-4">
              <ShoppingBag size={32} strokeWidth={1.3} className="text-slate-300" />
            </div>
            <p className="text-sm font-bold text-slate-500 mb-4">{pageText.profile.myOrdersPage.notRegisteredOrder}</p>
            <Link to="/shop" className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-primary text-white text-sm font-bold shadow-md shadow-primary/20 hover:shadow-lg transition-all">
              {pageText.profile.myOrdersPage.registerFirstOrder}
            </Link>
          </div>
        ) : (
          orders.map((order) => {
            const style = getStatusStyle(order.status_code);
            return (
              <div
                key={order.id}
                className={`${style.card} rounded-2xl ring-1 ring-black/[0.05] hover:ring-black/[0.08] hover:shadow-lg hover:shadow-black/[0.04] transition-all duration-300 overflow-hidden`}
              >
                {/* ردیف بالا */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-5 pb-4">
                  <div className="flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-xl bg-slate-50 ring-1 ring-black/[0.04] flex items-center justify-center text-sm font-extrabold text-slate-500">
                      #{order.id}
                    </div>
                    <div>
                      <h3 className="text-[15px] font-bold text-slate-800">
                        {order.type_display || pageText.profile.myOrdersPage.registerPrint}
                      </h3>
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-medium mt-0.5">
                        <Calendar size={11} />
                        {new Date(order.created_at).toLocaleDateString('en-GB')}
                      </div>
                    </div>
                  </div>

                  {/* بج وضعیت */}
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold self-start sm:self-auto ${style.badge}`}>
                    <div className={`w-1.5 h-1.5 rounded-full animate-pulse ${style.dot}`} />
                    {order.status}
                  </div>
                </div>

                {/* ردیف پایین */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 px-5 py-3.5 border-t border-slate-100/80 bg-slate-50/30">
                  <div className="flex items-center gap-2 text-[11px] font-medium text-slate-500 bg-white px-3 py-2 rounded-lg ring-1 ring-black/[0.04]">
                    <MapPin size={13} className="text-slate-400 shrink-0" />
                    <span className="truncate max-w-[220px]">{order.address || pageText.profile.myOrdersPage.notRegisteredAddress}</span>
                  </div>

                  <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                    <div className="text-left">
                      <span className="block text-[9px] text-slate-400 font-medium">{pageText.profile.myOrdersPage.totalPrice}</span>
                      <span className="text-base font-extrabold text-slate-700 tabular-nums dir-ltr">
                        {new Intl.NumberFormat('fa-IQ').format(order.total_price)}
                        <span className="text-[10px] font-bold text-slate-400 mr-1">{globalText.currency}</span>
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <Link
                        to={`/profile/orders/${order.id}/quotation`}
                        className="w-9 h-9 flex items-center justify-center rounded-lg text-slate-400 ring-1 ring-black/[0.06] hover:text-primary hover:ring-primary/30 hover:bg-primary/5 transition-all duration-200"
                        data-tip="پیش‌فاکتور"
                      >
                        <Printer size={15} />
                      </Link>
                      <Link
                        to={`/profile/orders/${order.id}/invoice`}
                        className="w-9 h-9 hidden sm:flex items-center justify-center rounded-lg text-slate-400 ring-1 ring-black/[0.06] hover:text-emerald-600 hover:ring-emerald-300 hover:bg-emerald-50 transition-all duration-200"
                        data-tip="فاکتور نهایی"
                      >
                        <FileCheck size={15} />
                      </Link>
                      <Link
                        to={`/profile/orders/${order.id}`}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-white text-xs font-bold shadow-sm shadow-primary/15 hover:shadow-md hover:shadow-primary/25 hover:-translate-y-[1px] active:translate-y-0 transition-all duration-200"
                      >
                        {pageText.profile.myOrdersPage.details}
                        <ChevronLeft size={14} />
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default MyOrdersPage;