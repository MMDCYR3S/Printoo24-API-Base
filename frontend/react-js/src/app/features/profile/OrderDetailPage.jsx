import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Download, FileText, Layers, MapPin, User, Package, DollarSign } from 'lucide-react';
import { profileService } from '../../services/profileService';

// --- Helper Functions ---
const formatDate = (dateString) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatPrice = (price) => {
  if (!price) return '0';
  return new Intl.NumberFormat('fa-IQ').format(Number(price));
};

const OrderDetailPage = () => {
  const { id } = useParams();
  
  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['order-detail', id],
    queryFn: () => profileService.getOrderDetails(id),
  });

  if (isLoading) return <div className="text-center py-20"><span className="loading loading-spinner text-primary loading-lg"></span></div>;
  if (isError || !order) return <div className="text-center py-20 text-error font-bold">مشکلی در دریافت اطلاعات سفارش پیش آمده است.</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 1. Header Section */}
      <header className="flex items-center gap-3 border-b border-slate-100 pb-4">
        <Link to="/profile/orders" className="btn btn-circle btn-sm btn-ghost hover:bg-slate-100 transition-colors">
          <ArrowRight size={20} className="text-slate-600"/>
        </Link>
        <div>
          <h1 className="text-xl font-black text-slate-800 flex items-center gap-2">
            جزئیات سفارش <span className="dir-ltr text-primary">#{order.id}</span>
          </h1>
          <div className="text-xs text-slate-400 mt-1">
             ثبت شده در: <span className="dir-ltr">{formatDate(order.created_at)}</span>
          </div>
        </div>
      </header>

      {/* 2. Info Grid (Status, Address, User) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Status & Price Card */}
        <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm flex flex-col justify-between gap-4">
          <div>
            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Package size={14}/> وضعیت فعلی</div>
            <div className="text-lg font-bold text-slate-800 badge badge-lg badge-primary badge-outline w-full py-4">
              {order.current_status}
            </div>
          </div>
          <div>
            <div className="text-xs text-slate-400 mb-1 flex items-center gap-1"><DollarSign size={14}/> مبلغ کل</div>
            <div className="text-2xl font-black text-primary dir-ltr">
              {formatPrice(order.total_price)} <span className="text-sm font-bold text-slate-500">IQD</span>
            </div>
          </div>
        </div>

        {/* User Info Card */}
        <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm lg:col-span-2 space-y-4">
          <h3 className="font-bold text-slate-700 text-sm border-b border-slate-50 pb-2 mb-2 flex items-center gap-2">
            <User size={16} className="text-primary"/> اطلاعات گیرنده
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            {order.recipient_name && (
              <div className="flex flex-col">
                <span className="text-slate-400 text-xs mb-1">نام تحویل گیرنده:</span>
                <span className="font-medium text-slate-800">{order.recipient_name}</span>
              </div>
            )}
             {order.recipient_phone && (
              <div className="flex flex-col">
                <span className="text-slate-400 text-xs mb-1">شماره تماس:</span>
                <span className="font-medium text-slate-800 dir-ltr text-right">{order.recipient_phone}</span>
              </div>
            )}
             {order.company_name && (
              <div className="flex flex-col md:col-span-2">
                <span className="text-slate-400 text-xs mb-1">نام شرکت:</span>
                <span className="font-medium text-slate-800">{order.company_name}</span>
              </div>
            )}
             {order.address_detail && (
              <div className="flex flex-col md:col-span-2 bg-slate-50 p-3 rounded-xl">
                <span className="text-slate-400 text-xs mb-1 flex items-center gap-1"><MapPin size={12}/> آدرس تحویل:</span>
                <span className="font-medium text-slate-700 leading-6">{order.address_detail}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. Order Items List */}
      <div className="space-y-4">
        <h2 className="font-bold text-slate-700 pr-2 flex items-center gap-2">
          <Layers size={18} className="text-primary"/> اقلام سفارش
        </h2>
        
        {order.items?.map((item) => (
          <div key={item.id} className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
            {/* Item Header */}
            <div className="bg-slate-50 p-4 border-b border-slate-100 flex flex-wrap justify-between items-center gap-2">
              <div className="font-bold text-slate-800 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-primary"></div>
                {item.product_name || item.name}
              </div>
              <div className="flex items-center gap-3">
                 <span className="badge badge-neutral text-xs px-3">تعداد: {item.quantity}</span>
                 <span className="font-bold text-primary text-sm dir-ltr">
                    {formatPrice(item.price)} IQD
                 </span>
              </div>
            </div>
            
            <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Col: Specifications */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 border-b border-slate-50 pb-1">مشخصات سفارش</h4>
                
                {/* Dimensions */}
                {(item.specifications?.width > 0 || item.specifications?.height > 0) && (
                   <div className="flex justify-between items-center bg-slate-50 px-3 py-2 rounded-lg text-sm">
                      <span className="text-slate-500">ابعاد (cm):</span>
                      <span className="font-bold dir-ltr text-slate-800">
                        {item.specifications.width} × {item.specifications.height}
                      </span>
                   </div>
                )}

                {/* Options List - FIXED for Object Handling */}
                {item.specifications?.options?.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {item.specifications.options.map((opt, i) => {
                      // FIX: Check if opt is an object {name, value} or a string
                      const label = typeof opt === 'object' && opt !== null 
                        ? `${opt.name}: ${opt.value}` 
                        : opt;
                        
                      return (
                        <span key={i} className="badge badge-ghost badge-sm text-slate-600 bg-slate-100 border-slate-200">
                          {label}
                        </span>
                      );
                    })}
                  </div>
                )}
                
                {/* Description */}
                {item.description && (
                  <div className="text-sm text-slate-500 bg-orange-50/50 p-3 rounded-lg border border-orange-100 mt-2">
                    <span className="font-bold text-orange-400 block text-xs mb-1">توضیحات:</span>
                    {item.description}
                  </div>
                )}
              </div>

              {/* Right Col: Files */}
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 border-b border-slate-50 pb-1">فایل‌های ضمیمه</h4>
                <div className="space-y-2">
                  {item.files?.length > 0 ? (
                    item.files.map((file) => (
                      <a 
                        key={file.id} 
                        href={file.file_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center gap-3 p-3 rounded-xl border border-slate-200 hover:border-primary hover:bg-primary/5 transition-all group bg-slate-50/50"
                      >
                        <div className="p-2 bg-white rounded-lg shadow-sm group-hover:text-primary text-slate-400 transition-colors">
                          <FileText size={18}/>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-bold text-sm text-slate-700 truncate">{file.type_name || 'فایل ضمیمه'}</div>
                          <div className="text-[10px] text-slate-400">
                            {formatDate(file.uploaded_at)} • برای دانلود کلیک کنید
                          </div>
                        </div>
                        <Download size={16} className="text-slate-300 group-hover:text-primary transition-colors"/>
                      </a>
                    ))
                  ) : (
                    <div className="text-center py-6 bg-slate-50 rounded-xl border border-dashed border-slate-200 text-slate-400 text-sm">
                      فایلی برای این آیتم ثبت نشده است.
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