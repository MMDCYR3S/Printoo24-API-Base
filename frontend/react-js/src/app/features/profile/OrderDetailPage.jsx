import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Download, FileText, Layers, Printer, Calendar, Clock, CreditCard } from 'lucide-react';
import { profileService } from '../../services/profileService';

const OrderDetailPage = () => {
  const { id } = useParams();
  
  // دریافت جزئیات سفارش
  const { data: order, isLoading } = useQuery({
    queryKey: ['order-detail', id],
    queryFn: () => profileService.getOrderDetails(id),
  });

  const getStatusColor = (status) => {
    if (!status) return 'text-slate-500 bg-slate-100';
    if (status.includes('تحویل') || status.includes('تکمیل')) return 'text-emerald-600 bg-emerald-50 border border-emerald-100';
    if (status.includes('چاپ') || status.includes('آماده')) return 'text-amber-600 bg-amber-50 border border-amber-100';
    if (status.includes('لغو')) return 'text-red-600 bg-red-50 border border-red-100';
    return 'text-blue-600 bg-blue-50 border border-blue-100';
  };

  if (isLoading) return <div className="flex justify-center py-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (!order) return <div className="text-center py-20 text-error font-bold">سفارش یافت نشد یا دسترسی ندارید.</div>;

  return (
    <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
      
      {/* هدر و دکمه بازگشت */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-3">
          <Link to="/profile/orders" className="btn btn-circle btn-sm btn-ghost hover:bg-slate-100"><ArrowRight size={20}/></Link>
          <div>
            <h1 className="text-xl font-black text-slate-800 flex items-center gap-2">
              جزئیات سفارش <span className="font-mono text-primary text-2xl">#{order.id}</span>
            </h1>
            <span className="text-xs text-slate-400">تاریخ ثبت: {new Date(order.created_at).toLocaleDateString('fa-IR')}</span>
          </div>
        </div>
        
        {/* دکمه مشاهده پیش‌فاکتور */}
        <Link 
          to={`/profile/orders/quotation/${order.id}`} 
          className="btn btn-outline btn-primary gap-2 rounded-xl shadow-sm hover:shadow-md transition-all w-full md:w-auto"
        >
          <Printer size={18} /> مشاهده و چاپ پیش‌فاکتور
        </Link>
      </div>

      {/* کارت خلاصه وضعیت */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* وضعیت */}
        <div className={`p-5 rounded-3xl flex items-center gap-4 ${getStatusColor(order.status_display)}`}>
           <div className="p-3 bg-white/50 rounded-2xl backdrop-blur-sm"><Clock size={24}/></div>
           <div>
             <span className="text-xs opacity-70 font-bold block mb-1">وضعیت فعلی</span>
             <span className="text-lg font-black">{order.status_display}</span>
           </div>
        </div>

        {/* مبلغ */}
        <div className="p-5 rounded-3xl bg-slate-800 text-white flex items-center gap-4 relative overflow-hidden">
           <div className="absolute top-0 left-0 w-20 h-20 bg-white/5 rounded-full blur-2xl -translate-x-1/2 -translate-y-1/2"></div>
           <div className="p-3 bg-white/10 rounded-2xl backdrop-blur-sm"><CreditCard size={24}/></div>
           <div>
             <span className="text-xs text-slate-400 font-bold block mb-1">مبلغ کل سفارش</span>
             <div className="flex items-baseline gap-1 dir-ltr">
                <span className="text-2xl font-black tracking-tight">{new Intl.NumberFormat('fa-IQ').format(order.total_price)}</span>
                <span className="text-xs opacity-50">IQD</span>
             </div>
           </div>
        </div>

        {/* آدرس (اگر هست) */}
        {order.address && (
           <div className="p-5 rounded-3xl bg-white border border-slate-200 flex items-center gap-4">
              <div className="p-3 bg-slate-50 text-slate-400 rounded-2xl"><Layers size={24}/></div>
              <div className="overflow-hidden">
                <span className="text-xs text-slate-400 font-bold block mb-1">آدرس ثبت شده</span>
                <span className="text-sm font-bold text-slate-700 truncate block">شناسه آدرس: {order.address}</span>
              </div>
           </div>
        )}
      </div>

      {/* لیست اقلام سفارش */}
      <div className="space-y-4">
        <h2 className="font-bold text-slate-800 pr-2 flex items-center gap-2 text-lg">
          <span className="w-2 h-8 rounded-full bg-primary"></span>
          اقلام سفارش
        </h2>
        
        {order.order_item?.map((item) => (
          <div key={item.id} className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden group hover:border-primary/30 transition-colors">
            {/* هدر آیتم */}
            <div className="bg-slate-50 p-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-3">
              <span className="font-black text-slate-800 flex items-center gap-2 text-lg">
                <Layers size={20} className="text-primary"/> {item.product_name}
              </span>
              <span className="badge badge-neutral text-xs font-bold px-3 py-2 h-auto">تعداد: {item.quantity}</span>
            </div>
            
            <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* ستون مشخصات فنی */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span> مشخصات محصول
                </h4>
                <div className="bg-slate-50 rounded-2xl p-4 space-y-3 border border-slate-100">
                  {item.specs?.material && (
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500">جنس کاغذ:</span>
                      <span className="font-bold text-slate-800">{item.specs.material}</span>
                    </div>
                  )}
                  {item.specs?.dimensions && (
                    <div className="flex justify-between items-center text-sm border-t border-slate-200 pt-3">
                      <span className="text-slate-500">ابعاد نهایی:</span>
                      <span className="font-bold text-slate-800 dir-ltr font-mono">{item.specs.dimensions}</span>
                    </div>
                  )}
                  
                  {/* آپشن‌ها */}
                  {item.specs?.options && item.specs.options.length > 0 && (
                    <div className="pt-3 border-t border-slate-200">
                      <span className="text-xs text-slate-400 block mb-2">خدمات پس از چاپ:</span>
                      <div className="flex flex-wrap gap-2">
                        {item.specs.options.map((opt, i) => (
                          <span key={i} className="badge badge-ghost text-xs border-slate-200 bg-white text-slate-600">
                            {opt}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* ستون فایل‌ها */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span> فایل‌های ارسالی شما
                </h4>
                <div className="space-y-3">
                  {item.design_files?.length > 0 ? (
                    item.design_files.map((file) => (
                      <a 
                        key={file.id} 
                        href={file.file_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center gap-4 p-3 rounded-2xl border border-dashed border-slate-300 hover:border-primary hover:bg-primary/5 transition-all group/file relative overflow-hidden"
                      >
                        <div className="p-3 bg-white border border-slate-100 rounded-xl text-slate-400 group-hover/file:text-primary transition-colors shadow-sm">
                          <FileText size={20}/>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-bold text-sm text-slate-700 truncate">{file.requirement_name || 'فایل طراحی'}</div>
                          <div className="text-[10px] text-slate-400 mt-0.5">برای دانلود کلیک کنید</div>
                        </div>
                        <div className="bg-slate-100 p-2 rounded-lg text-slate-400 group-hover/file:bg-primary group-hover/file:text-white transition-colors">
                           <Download size={16} />
                        </div>
                      </a>
                    ))
                  ) : (
                    <div className="text-center p-6 border border-dashed border-slate-200 rounded-2xl bg-slate-50 text-slate-400 text-sm">
                      هیچ فایلی برای این آیتم آپلود نشده است.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrderDetailPage;