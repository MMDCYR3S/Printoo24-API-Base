import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Download, FileText, Layers } from 'lucide-react';
import { profileService } from '../../services/profileService';

const OrderDetailPage = () => {
  const { id } = useParams();
  const { data: order, isLoading } = useQuery({
    queryKey: ['order-detail', id],
    queryFn: () => profileService.getOrderDetails(id),
  });

  if (isLoading) return <div className="text-center py-20"><span className="loading loading-spinner text-primary"></span></div>;
  if (!order) return <div className="text-center py-20 text-error">سفارش یافت نشد.</div>;

  return (
    <div className="space-y-6">
      {/* هدر و دکمه بازگشت */}
      <div className="flex items-center gap-3">
        <Link to="/profile/orders" className="btn btn-circle btn-sm btn-ghost"><ArrowRight size={20}/></Link>
        <h1 className="text-xl font-black text-slate-800">جزئیات سفارش #{order.id}</h1>
      </div>

      {/* خلاصه وضعیت */}
      <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
           <div className="text-sm text-slate-400 mb-1">وضعیت سفارش</div>
           <div className="text-xl font-bold text-slate-800">{order.status_display}</div>
        </div>
        <div className="text-center md:text-left">
           <div className="text-sm text-slate-400 mb-1">مبلغ کل</div>
           <div className="text-2xl font-black text-primary dir-ltr">{new Intl.NumberFormat('fa-IQ').format(order.total_price)} IQD</div>
        </div>
      </div>

      {/* لیست آیتم‌ها */}
      <div className="space-y-4">
        <h2 className="font-bold text-slate-700 pr-2">اقلام سفارش</h2>
        {order.order_item?.map((item) => (
          <div key={item.id} className="bg-white rounded-3xl border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 p-4 border-b border-slate-100 flex justify-between items-center">
              <span className="font-bold text-slate-800 flex items-center gap-2">
                <Layers size={18} className="text-primary"/> {item.product_name}
              </span>
              <span className="badge badge-neutral text-xs">تعداد: {item.quantity}</span>
            </div>
            
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* مشخصات فنی */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-3">مشخصات فنی</h4>
                <ul className="space-y-2 text-sm">
                  {item.specs?.material && <li className="flex justify-between border-b border-slate-50 pb-1"><span>جنس:</span> <span className="font-medium">{item.specs.material}</span></li>}
                  {item.specs?.dimensions && <li className="flex justify-between border-b border-slate-50 pb-1"><span>ابعاد:</span> <span className="font-medium dir-ltr">{item.specs.dimensions}</span></li>}
                  {item.specs?.options?.map((opt, i) => (
                    <li key={i} className="text-slate-600 bg-slate-50 px-2 py-1 rounded inline-block ml-1 text-xs">{opt}</li>
                  ))}
                </ul>
              </div>

              {/* فایل‌های طراحی */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase mb-3">فایل‌های ضمیمه</h4>
                <div className="space-y-2">
                  {item.design_files?.map((file) => (
                    <a 
                      key={file.id} 
                      href={file.file_url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:border-primary hover:bg-primary/5 transition-all group"
                    >
                      <div className="p-2 bg-slate-100 rounded-lg group-hover:bg-white text-slate-500 group-hover:text-primary"><FileText size={20}/></div>
                      <div className="flex-1">
                        <div className="font-bold text-sm text-slate-700">{file.requirement_name}</div>
                        <div className="text-[10px] text-slate-400">برای دانلود کلیک کنید</div>
                      </div>
                      <Download size={16} className="text-slate-300 group-hover:text-primary"/>
                    </a>
                  ))}
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