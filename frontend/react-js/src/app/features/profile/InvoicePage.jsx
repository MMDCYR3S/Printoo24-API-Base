import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, Receipt, CreditCard, Info } from 'lucide-react';
import { profileService } from '../../services/profileService';
import { formatCurrency } from '../../utils/formatters';
import globalText from '../../lang/global.json';

const InvoicePage = () => {
  const { id } = useParams();

  const { data: invoice, isLoading, isError, error } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => profileService.getInvoiceByOrder(id),
    retry: false,
  });

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20 print:hidden">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  if (isError || !invoice) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-6 max-w-lg mx-auto text-center animate-in fade-in duration-500 print:hidden">
        <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-2">
          <Receipt size={48} />
        </div>
        <h2 className="text-xl font-black text-slate-700">فاکتوری یافت نشد!</h2>
        <p className="text-slate-500 text-sm leading-relaxed">
          {error?.response?.data?.detail || "فاکتور تنها در صورتی نمایش داده می‌شود که وضعیت سفارش تسویه کامل یا نهایی شده باشد."}
        </p>
        <Link to={`/profile/orders/${id}`} className="btn btn-primary rounded-xl px-8 shadow-lg shadow-primary/20 mt-4">
          بازگشت به سفارش
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-10 print:pb-0 print:bg-white animate-in fade-in duration-500">
      
      {/* ترفند چاپ بدون تخریب ظاهر: 
        این کد تمام استایل‌ها، بک‌گراندها و رنگ‌های ملایم رو دقیقاً همونطور که 
        روی مانیتور می‌بینی برای چاپ هم حفظ می‌کنه، اما کل سایت (هدر/فوتر) رو مخفی می‌کنه.
      */}
      <style type="text/css" media="print">
        {`
          @page { size: A4 portrait; margin: 15mm; }
          body { 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
            background-color: white !important;
          }
          body * { visibility: hidden !important; }
          #printable-invoice, #printable-invoice * { visibility: visible !important; }
          #printable-invoice {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            margin: 0 !important;
            box-shadow: none !important;
          }
        `}
      </style>

      {/* اکشن بار (مخفی در چاپ) */}
      <div className="max-w-4xl mx-auto mb-6 flex justify-between items-center print:hidden">
        <Link to={`/profile/orders/${id}`} className="btn btn-ghost text-slate-500 hover:bg-slate-100 rounded-xl gap-2">
          <ChevronRight size={18} /> بازگشت به سفارش
        </Link>
        <button onClick={handlePrint} className="btn btn-primary rounded-xl px-6 shadow-lg shadow-primary/20 gap-2">
          <Printer size={18} /> چاپ فاکتور
        </button>
      </div>

      {/* خود فاکتور - تمام کلاس‌های زیباسازی اینجا حفظ شدن */}
      <div 
        id="printable-invoice" 
        className="max-w-4xl mx-auto bg-white rounded-3xl shadow-2xl shadow-slate-200/50 overflow-hidden border border-slate-100"
      >
        
        {/* هدر فاکتور */}
        <div className="px-8 py-10 border-b-2 border-slate-50 flex flex-row justify-between items-center gap-6">
          <div className="space-y-2">
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">فاکتور نهایی</h1>
            <p className="text-slate-400 text-sm font-medium">سرویس چاپ آنلاین Printoo24</p>
          </div>
          
          <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-left min-w-[250px]">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-slate-400 font-bold">شماره فاکتور:</span>
              <span className="text-sm font-black text-slate-700 dir-ltr">{invoice.invoice_number}</span>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-slate-400 font-bold">تاریخ صدور:</span>
              <span className="text-sm font-semibold text-slate-600">
                {new Date(invoice.issued_at).toLocaleDateString('fa-IR')}
              </span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-slate-200 border-dashed">
              <span className="text-xs text-slate-400 font-bold">وضعیت:</span>
              <span className="badge badge-success bg-success/10 text-success border-none font-bold text-xs px-3 py-3 rounded-lg">
                {invoice.status_display}
              </span>
            </div>
          </div>
        </div>

        {/* بدنه فاکتور (لیست مبالغ) */}
        <div className="p-8">
          <div className="space-y-0 text-sm text-slate-600">
            <div className="flex justify-between items-center py-4 border-b border-dashed border-slate-200 hover:bg-slate-50/50 px-2 transition-colors">
              <span className="font-semibold text-slate-700">مجموع مبلغ اقلام سفارش</span>
              <span className="font-bold dir-ltr">
                {formatCurrency(invoice.items_amount)} <span className="text-xs text-slate-400">{globalText.currency}</span>
              </span>
            </div>

            <div className="flex justify-between items-center py-4 border-b border-dashed border-slate-200 hover:bg-slate-50/50 px-2 transition-colors">
              <span className="font-semibold text-slate-700">هزینه خدمات / جانبی</span>
              <span className="font-bold dir-ltr">
                {formatCurrency(invoice.services_amount)} <span className="text-xs text-slate-400">{globalText.currency}</span>
              </span>
            </div>

            <div className="flex justify-between items-center py-4 border-b border-dashed border-slate-200 hover:bg-slate-50/50 px-2 transition-colors">
              <span className="font-semibold text-slate-700">مالیات بر ارزش افزوده</span>
              <span className="font-bold dir-ltr text-slate-500">
                + {formatCurrency(invoice.tax_amount)} <span className="text-xs text-slate-400">{globalText.currency}</span>
              </span>
            </div>

            <div className="flex justify-between items-center py-4 px-2 transition-colors">
              <span className="font-semibold text-error">تخفیف اعمال شده</span>
              <span className="font-bold dir-ltr text-error">
                - {formatCurrency(invoice.discount_amount)} <span className="text-xs text-slate-400">{globalText.currency}</span>
              </span>
            </div>
          </div>
        </div>

        {/* بخش جمع‌بندی مالی (حفظ بک‌گراندهای ملایم) */}
        <div className="bg-slate-50 p-8 grid grid-cols-1 md:grid-cols-3 gap-6 border-t border-slate-100">
          <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-sm flex flex-col justify-center items-center text-center">
            <span className="text-xs text-slate-400 font-bold mb-1">مبلغ نهایی فاکتور</span>
            <span className="text-xl font-black text-slate-800 dir-ltr">
              {formatCurrency(invoice.final_amount)} <span className="text-sm font-medium text-slate-400">{globalText.currency}</span>
            </span>
          </div>

          <div className="bg-success/5 p-5 rounded-2xl border border-success/10 flex flex-col justify-center items-center text-center">
            <span className="text-xs text-success/70 font-bold mb-1 flex items-center gap-1"><CreditCard size={14} className="print:hidden"/> پرداخت شده</span>
            <span className="text-xl font-black text-success dir-ltr">
              {formatCurrency(invoice.paid_amount)} <span className="text-sm font-medium opacity-70">{globalText.currency}</span>
            </span>
          </div>

          <div className={`p-5 rounded-2xl border flex flex-col justify-center items-center text-center ${invoice.remaining_amount < 0 ? 'bg-info/5 border-info/10' : invoice.remaining_amount > 0 ? 'bg-error/5 border-error/10' : 'bg-slate-100 border-slate-200'}`}>
            <span className={`text-xs font-bold mb-1 ${invoice.remaining_amount !== 0 ? 'text-slate-600' : 'text-slate-400'}`}>
              {invoice.remaining_amount < 0 ? 'بستانکار (اضافه پرداختی)' : invoice.remaining_amount > 0 ? 'بدهی (باقیمانده)' : 'مانده حساب'}
            </span>
            <span className={`text-xl font-black dir-ltr ${invoice.remaining_amount < 0 ? 'text-info' : invoice.remaining_amount > 0 ? 'text-error' : 'text-slate-500'}`}>
              {formatCurrency(Math.abs(invoice.remaining_amount))} <span className="text-sm font-medium opacity-70">{globalText.currency}</span>
            </span>
          </div>
        </div>

        {/* توضیحات */}
        {invoice.description && (
          <div className="p-8 bg-white border-t border-slate-50">
            <div className="flex items-start gap-3 bg-slate-50/50 p-4 rounded-2xl border border-slate-100">
              <Info size={20} className="text-slate-400 flex-shrink-0 mt-0.5 print:hidden" />
              <div>
                <span className="block text-xs font-bold text-slate-500 mb-1">توضیحات فاکتور:</span>
                <p className="text-sm text-slate-600 leading-relaxed text-justify">
                  {invoice.description}
                </p>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default InvoicePage;