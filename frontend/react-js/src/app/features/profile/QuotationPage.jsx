import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, AlertCircle, Phone, MapPin, Instagram } from 'lucide-react';
import { profileService } from '../../services/profileService';

// وارد کردن فایل‌های ترجمه
import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const formatCurrency = (val) => new Intl.NumberFormat('fa-IQ').format(val);

const QuotationPage = () => {
  const { id } = useParams();

  const { data: quotation, isLoading, isError, error } = useQuery({
    queryKey: ['quotation', id],
    queryFn: () => profileService.getQuotationByOrder(id),
    retry: 1,
  });

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-20 print:hidden" dir="rtl">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  if (isError || !quotation) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-6 max-w-lg mx-auto text-center animate-in fade-in duration-500 print:hidden" dir="rtl">
        <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-2">
          <AlertCircle size={48} />
        </div>
        <h2 className="text-xl font-black text-slate-700">{pageText.order.quotationPage.notFound}</h2>
        <p className="text-slate-500 text-sm leading-relaxed">
          {error?.response?.data?.detail || "ممکن است پیش‌فاکتور حذف شده باشد یا مشکلی در دریافت اطلاعات وجود داشته باشد."}
        </p>
        <Link to={`/profile/orders/${id}`} className="btn btn-primary rounded-xl px-8 shadow-lg shadow-primary/20 mt-4">
          {pageText.order.quotationPage.backToOrder}
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-10 print:pb-0 print:bg-white animate-in fade-in duration-500 bg-slate-50 flex flex-col items-center" dir="rtl">
      
      {/* استایل‌های جادویی پرینت سایز A4 */}
      <style type="text/css" media="print">
        {`
          @page { 
            size: A4 portrait; 
            margin: 0; 
          }
          body { 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
            background-color: white !important;
            margin: 0 !important;
            padding: 0 !important;
          }
          body * { visibility: hidden !important; }
          #printable-invoice, #printable-invoice * { visibility: visible !important; }
          
          #printable-invoice {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 210mm !important; 
            min-height: 297mm !important; 
            margin: 0 auto !important;
            padding: 10mm 0 !important; 
            box-shadow: none !important;
            border: none !important;
            background: white !important;
          }
        `}
      </style>

      {/* اکشن بار (مخفی در چاپ) */}
      <div className="w-full max-w-[210mm] pt-6 mb-6 flex justify-between items-center print:hidden px-4">
        <Link to={`/profile/orders/${id}`} className="btn btn-ghost text-slate-500 hover:bg-slate-200 rounded-xl gap-2">
          <ChevronRight size={18} /> {pageText.order.quotationPage.backBtn}
        </Link>
        <button onClick={handlePrint} className="btn bg-primary text-primary-content hover:bg-primary/90 rounded-xl px-8 shadow-lg shadow-primary/20 gap-2 border-none">
          <Printer size={18} /> {pageText.order.quotationPage.printBtn}
        </button>
      </div>

      {/* بدنه اصلی پیش‌فاکتور */}
      <div 
        id="printable-invoice" 
        className="w-full max-w-[210mm] min-h-[297mm] mx-auto bg-white shadow-2xl shadow-slate-200/50 relative border border-slate-100 print:border-none flex flex-col"
      >
        
        {/* هدر زرد رنگ بالای فاکتور */}
        <div className="bg-neutral m-4 print:mx-6 rounded-[2rem] p-6 relative flex flex-row items-center justify-between overflow-hidden min-h-[140px] shrink-0">
          <div className="absolute -right-8 top-1/2 -translate-y-1/2 w-40 h-40 bg-primary rotate-45 border-4 border-white flex items-center justify-center shadow-lg print:shadow-none">
            <span className="text-primary-content -rotate-45 font-black text-3xl tracking-tighter">P24</span>
          </div>
          <div className="flex-1 text-center mr-36 text-white">
            <h1 className="text-4xl font-black mb-4 tracking-tight">{pageText.order.quotationPage.brandName}</h1>
            <div className="flex justify-center items-center gap-8 font-bold text-sm">
              <span className="flex items-center gap-1 dir-ltr"><Phone size={18} className="mr-1"/> 021 - 1234 5678</span>
              <span className="flex items-center gap-1"><MapPin size={18} className="ml-1"/> {pageText.order.quotationPage.brandSub}</span>
            </div>
          </div>
        </div>

        {/* اطلاعات خریدار و پیش‌فاکتور */}
        <div className="px-12 py-6 flex justify-between items-start shrink-0">
          <div className="text-right">
            <h2 className="text-5xl text-blue-500 font-normal tracking-wide mb-2">Quotation</h2>
            <p className="text-slate-700 font-bold text-lg">{pageText.order.quotationPage.pageTitle} رسمی</p>
          </div>
          <div className="text-base space-y-3 text-right border-l-4 border-neutral pl-6">
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.quotationPage.customerInfoTitle}:</span> 
              <span className="font-semibold text-slate-600">{quotation.customer_name}</span>
            </div>
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.quotationPage.pageTitle} {pageText.order.quotationPage.numberLabel}</span> 
              <span className="font-black text-blue-500 dir-ltr text-lg">{quotation.quotation_number}</span>
            </div>
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.quotationPage.dateLabel}</span> 
              <span className="font-semibold text-slate-600 dir-ltr">
                {new Date(quotation.created_at).toLocaleDateString('fa-IR')}
              </span>
            </div>
          </div>
        </div>

        {/* جدول اقلام */}
        <div className="px-12 mt-2 flex-grow">
          <table className="w-full text-base text-right border-collapse">
            <thead>
              <tr className="border-y-4 border-neutral text-slate-700 bg-slate-50/50">
                <th className="py-3 px-3 font-black w-12">{pageText.order.quotationPage.tableRow}</th>
                <th className="py-3 px-3 font-black">{pageText.order.quotationPage.tableDescription}</th>
                <th className="py-3 px-3 font-black w-20">{pageText.order.quotationPage.tableQuantity}</th>
                <th className="py-3 px-3 font-black w-36 text-left">{pageText.order.quotationPage.tableUnitPrice}</th>
                <th className="py-3 px-3 font-black w-40 text-left">{pageText.order.quotationPage.tableTotalPrice}</th>
              </tr>
            </thead>
            <tbody className="text-slate-800">
              <tr className="border-b border-slate-200">
                <td className="py-4 px-3 font-bold align-top">۱</td>
                <td className="py-4 px-3 font-semibold align-top text-right">
                  <span className="font-bold block mb-1 text-lg">{quotation.product_name}</span>
                  {quotation.product_snapshot?.meta?.size_info && (
                    <span className="text-xs font-medium text-slate-500 ml-2 block mt-2">
                      <span className="font-bold text-slate-700">{pageText.order.quotationPage.dimensions}</span> {quotation.product_snapshot.meta.size_info.size_name}
                    </span>
                  )}
                  {quotation.product_snapshot?.options?.map((opt, idx) => (
                    <span key={idx} className="text-xs font-medium text-slate-500 ml-2 block mt-1">
                      <span className="font-bold text-slate-700">{opt.option_label}:</span> {opt.value.label}
                    </span>
                  ))}
                </td>
                <td className="py-4 px-3 font-medium align-top">{quotation.quantity}</td>
                <td className="py-4 px-3 dir-ltr text-left font-medium align-top">
                  {formatCurrency(quotation.total_price / quotation.quantity)}
                </td>
                <td className="py-4 px-3 dir-ltr text-left font-bold align-top">
                  {formatCurrency(quotation.total_price)}
                </td>
              </tr>
              <tr className="border-b-4 border-neutral bg-slate-50/30">
                <td colSpan="4" className="py-4 px-3 text-left font-black text-slate-800 text-lg">{pageText.order.quotationPage.totalPayable}</td>
                <td className="py-4 px-3 font-black dir-ltr text-left text-slate-800 text-lg">
                  {formatCurrency(quotation.total_price)} <span className="text-sm font-medium text-slate-500">{globalText.currency}</span>
                </td>
              </tr>
            </tbody>
          </table>
          
          {/* بخش توضیحات */}
          <div className="mt-6 text-sm bg-slate-50/50 py-3 px-4 rounded-xl border border-slate-100 print:border-none print:bg-transparent">
            <p className="text-slate-800 font-medium leading-relaxed">
              <span className="font-black text-primary">{pageText.order.quotationPage.notesTitle}</span> <br/>
              {pageText.order.quotationPage.note1} <br/>
              {pageText.order.quotationPage.note2}
            </p>
          </div>
        </div>

        {/* محافظت از شکسته شدن صفحه */}
        <div className="print:break-inside-avoid mt-auto pt-16 shrink-0 relative">
          
          {/* بخش پایینی: مهر و امضا + مبالغ نهایی */}
          <div className="px-12 relative flex justify-between items-end mb-6">
            {/* خط زرد جداکننده */}
            <div className="absolute bottom-16 left-12 right-12 h-[3px] bg-neutral print:bg-neutral z-0"></div>

            {/* مهر و امضا */}
            <div className="z-10 bg-white print:bg-white px-8 text-center pb-2">
              <div className="w-24 h-24 bg-secondary text-secondary-content rotate-45 mx-auto mb-6 flex items-center justify-center border-4 border-white shadow-sm print:border-2">
                <span className="-rotate-45 text-xs font-black text-center leading-relaxed">{pageText.order.quotationPage.sellerStamp}<br/>Printoo24</span>
              </div>
              <p className="font-black text-slate-800 text-sm">Stamp & Signature</p>
            </div>

            {/* خلاصه مبالغ (چون پیش فاکتوره فقط جمع کل رو نشون دادم) */}
            <div className="z-10 bg-white print:bg-white px-6 text-base w-80 space-y-3 pb-2">
              <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg">
                <span className="font-black text-blue-600 text-lg">مبلغ کل برآورد:</span>
                <span className="font-black text-blue-600 text-xl dir-ltr">
                  {formatCurrency(quotation.total_price)} <span className="text-sm">{globalText.currency}</span>
                </span>
              </div>
            </div>
          </div>

          {/* فوتر زرد پایین */}
          <div className="bg-neutral text-white font-black p-4 mx-6 print:mx-6 mb-4 rounded-[1.5rem] text-center flex justify-center items-center gap-2 text-lg">
            <Instagram size={22} /> <span className="mt-1 tracking-widest uppercase">printoo24_official</span>
          </div>

        </div>

      </div>
    </div>
  );
};

export default QuotationPage;