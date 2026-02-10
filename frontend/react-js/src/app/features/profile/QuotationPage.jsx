import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ArrowRight, Download, FileText } from 'lucide-react';
import { profileService } from '../../services/profileService';

const QuotationPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: quote, isLoading, isError } = useQuery({
    queryKey: ['quotation', id],
    queryFn: () => profileService.getQuotation(id),
    retry: 1,
  });

  // هندل کردن پرینت
  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <span className="loading loading-spinner loading-lg text-primary"></span>
        <p className="text-slate-500 animate-pulse">در حال صدور پیش‌فاکتور...</p>
      </div>
    );
  }

  if (isError || !quote) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center p-4">
        <FileText size={64} className="text-slate-200 mb-4" />
        <h2 className="text-xl font-bold text-slate-800">پیش‌فاکتور یافت نشد</h2>
        <p className="text-slate-500 mt-2 mb-6">ممکن است شناسه سفارش اشتباه باشد یا دسترسی نداشته باشید.</p>
        <button onClick={() => navigate(-1)} className="btn btn-outline">بازگشت</button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans">
      
      {/* نوار ابزار بالا (در پرینت حذف می‌شود) */}
      <div className="max-w-4xl mx-auto mb-6 flex justify-between items-center print:hidden">
        <button 
          onClick={() => navigate(-1)}
          className="btn btn-ghost btn-sm gap-2 text-slate-600"
        >
          <ArrowRight size={18} /> بازگشت
        </button>
        <button 
          onClick={handlePrint}
          className="btn btn-primary gap-2 shadow-lg shadow-primary/20"
        >
          <Printer size={18} /> چاپ / دانلود PDF
        </button>
      </div>

      {/* کاغذ A4 فاکتور */}
      <div className="max-w-4xl mx-auto bg-white shadow-2xl print:shadow-none print:w-full print:max-w-none rounded-none md:rounded-3xl overflow-hidden relative">
        
        {/* هدر رنگی */}
        <div className="h-3 bg-primary w-full print:bg-black"></div>

        <div className="p-8 md:p-12 print:p-0">
          
          {/* سربرگ */}
          <div className="flex justify-between items-start border-b-2 border-slate-100 pb-8 mb-8">
            <div>
              <h1 className="text-3xl font-black text-slate-900 mb-2">پیش‌فاکتور خدمات چاپ</h1>
              <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded text-sm font-bold print:border print:border-slate-300">
                وضعیت: {quote.status_display || 'صادر شده'}
              </span>
            </div>
            <div className="text-left text-slate-500 text-sm space-y-1">
              <div className="flex items-center gap-2 justify-end">
                <span className="font-bold text-slate-800">شماره:</span>
                <span className="font-mono text-lg">{quote.quotation_number}</span>
              </div>
              <div className="flex items-center gap-2 justify-end">
                <span className="font-bold text-slate-800">تاریخ صدور:</span>
                <span className="dir-ltr">{new Date(quote.created_at).toLocaleDateString('fa-IR')}</span>
              </div>
            </div>
          </div>

          {/* مشخصات طرفین */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 print:bg-transparent print:border-slate-300">
              <h3 className="text-slate-400 text-xs font-bold mb-3 uppercase tracking-wider">مشخصات خریدار</h3>
              <p className="text-xl font-bold text-slate-800 mb-1">{quote.customer_name}</p>
              {/* اگر آدرس یا تلفن در آبجکت باشد اینجا اضافه شود */}
            </div>
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 print:bg-transparent print:border-slate-300">
              <h3 className="text-slate-400 text-xs font-bold mb-3 uppercase tracking-wider">مشخصات محصول</h3>
              <p className="text-xl font-bold text-slate-800 mb-1">{quote.product_name}</p>
              <div className="flex gap-4 mt-2 text-sm text-slate-600">
                 <span>تراژ: <strong className="text-slate-900">{quote.quantity} عدد</strong></span>
              </div>
            </div>
          </div>

          {/* جدول جزئیات فنی */}
          <div className="mb-12">
            <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary"></span>
              مشخصات فنی سفارش
            </h3>
            <div className="overflow-hidden border border-slate-200 rounded-xl print:border-slate-300">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-slate-500 print:bg-slate-100">
                  <tr>
                    <th className="py-4 px-6 text-right font-bold">عنوان مشخصه</th>
                    <th className="py-4 px-6 text-left font-bold">مقدار / توضیحات</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr>
                    <td className="py-4 px-6 text-slate-600">ابعاد</td>
                    <td className="py-4 px-6 text-left font-bold text-slate-800 dir-ltr">
                      {quote.snapshot_details?.dimensions || '-'}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6 text-slate-600">جنس کاغذ / متریال</td>
                    <td className="py-4 px-6 text-left font-bold text-slate-800">
                      {quote.snapshot_details?.material || '-'}
                    </td>
                  </tr>
                  {quote.snapshot_details?.features?.map((feature, idx) => (
                    <tr key={idx}>
                      <td className="py-4 px-6 text-slate-600">آپشن {idx + 1}</td>
                      <td className="py-4 px-6 text-left font-bold text-slate-800">{feature}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* جمع کل */}
          <div className="flex justify-end mb-16">
            <div className="w-full md:w-1/2 lg:w-1/3 bg-slate-900 text-white p-6 rounded-2xl print:bg-white print:text-black print:border-2 print:border-black">
              <div className="flex justify-between items-center text-lg">
                <span className="opacity-80">مبلغ قابل پرداخت:</span>
                <span className="font-black text-2xl dir-ltr">
                  {Number(quote.total_price).toLocaleString()} <span className="text-sm font-normal opacity-70">IQD</span>
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-2 text-center print:hidden">
                این مبلغ شامل مالیات و عوارض قانونی می‌باشد.
              </p>
            </div>
          </div>

          {/* فوتر */}
          <div className="border-t border-slate-100 pt-8 text-center text-slate-400 text-sm print:text-xs">
            <p>این سند به صورت سیستمی صادر شده و فاقد مهر فیزیکی معتبر است.</p>
            <p className="mt-1 dir-ltr">www.printoo24.com</p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default QuotationPage;