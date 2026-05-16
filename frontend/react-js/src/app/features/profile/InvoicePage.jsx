import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, Receipt, Phone, MapPin, Instagram } from 'lucide-react';
import { profileService } from '../../services/profileService';
import { formatCurrency } from '../../utils/formatters';

import pageText from '../../lang/pages.json';
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
      <div className="flex justify-center py-20 print:hidden" dir="rtl">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  if (isError || !invoice) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-6 max-w-lg mx-auto text-center animate-in fade-in duration-500 print:hidden" dir="rtl">
        <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-2">
          <Receipt size={48} />
        </div>
        <h2 className="text-xl font-black text-slate-700">{pageText.order.invoicePage.invoiceNotFound}</h2>
        <p className="text-slate-500 text-sm leading-relaxed">
          {error?.response?.data?.detail || pageText.order.invoicePage.invoiceErrorHint}
        </p>
        <Link to={`/profile/orders/${id}`} className="btn btn-primary rounded-xl px-8 shadow-lg shadow-primary/20 mt-4">
          {pageText.order.invoicePage.backToOrder}
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
            margin: 0; /* حذف کامل هدر/فوتر و لینک‌های مرورگر */
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
            width: 210mm !important; /* دقیقاً عرض A4 */
            min-height: 297mm !important; /* دقیقاً ارتفاع A4 */
            margin: 0 auto !important;
            padding: 10mm 0 !important; /* پدینگ امن داخلی */
            box-shadow: none !important;
            border: none !important;
            background: white !important;
          }
        `}
      </style>

      {/* اکشن بار (مخفی در چاپ) */}
      <div className="w-full max-w-[210mm] pt-6 mb-6 flex justify-between items-center print:hidden px-4">
        <Link to={`/profile/orders/${id}`} className="btn btn-ghost text-slate-500 hover:bg-slate-200 rounded-xl gap-2">
          <ChevronRight size={18} /> {pageText.order.invoicePage.backToOrder}
        </Link>
        <button onClick={handlePrint} className="btn bg-primary text-primary-content hover:bg-primary/90 rounded-xl px-8 shadow-lg shadow-primary/20 gap-2 border-none">
          <Printer size={18} /> {pageText.order.invoicePage.printInvoice}
        </button>
      </div>

      {/* بدنه اصلی فاکتور 
        عرض کانتینر روی دسکتاپ همون سایز A4 (حدود 210mm) تنظیم شده تا تو مانیتور همون چیزی رو ببینی که تو پرینت درمیاد
      */}
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
            <h1 className="text-5xl font-black mb-4 tracking-tight">{pageText.order.invoicePage.brandName}</h1>
            <div className="flex justify-center items-center gap-8 font-bold text-sm">
              <span className="flex items-center gap-1 dir-ltr"><Phone size={18} className="mr-1"/> 021 - 1234 5678</span>
              <span className="flex items-center gap-1"><MapPin size={18} className="ml-1"/> {pageText.order.invoicePage.address}</span>
            </div>
          </div>
        </div>

        {/* اطلاعات خریدار و فاکتور */}
        <div className="px-12 py-6 flex justify-between items-start shrink-0">
          <div className="text-right">
            <h2 className="text-5xl text-red-500 font-normal tracking-wide mb-2">Invoice</h2>
            <p className="text-slate-700 font-bold text-lg">{pageText.order.invoicePage.invoiceTitle}</p>
          </div>
          <div className="text-base space-y-3 text-right border-l-4 border-neutral pl-6">
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.invoicePage.issuedFor}</span> 
              <span className="font-semibold text-slate-600">{invoice?.customer_name || pageText.order.invoicePage.defaultCustomer}</span>
            </div>
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.invoicePage.contactNumber}</span> 
              <span className="font-semibold text-slate-600 dir-ltr">{invoice?.customer_phone || '-'}</span>
            </div>
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.invoicePage.invoiceNumber}</span> 
              <span className="font-black text-red-500 dir-ltr text-lg">{invoice?.invoice_number}</span>
            </div>
            <div className="flex gap-3 justify-end items-center">
              <span className="font-bold text-slate-800">{pageText.order.invoicePage.issueDate}</span> 
              <span className="font-semibold text-slate-600 dir-ltr">
                {new Date(invoice?.issued_at || Date.now()).toLocaleDateString('fa-IR')}
              </span>
            </div>
          </div>
        </div>

        {/* جدول اقلام */}
        <div className="px-12 mt-2 flex-grow">
          <table className="w-full text-base text-right border-collapse">
            <thead>
              <tr className="border-y-4 border-neutral text-slate-700 bg-slate-50/50">
                <th className="py-3 px-3 font-black w-12">{pageText.order.invoicePage.tableRow}</th>
                <th className="py-3 px-3 font-black">{pageText.order.invoicePage.tableDescription}</th>
                <th className="py-3 px-3 font-black w-20">{pageText.order.invoicePage.tableQuantity}</th>
                <th className="py-3 px-3 font-black w-24">{pageText.order.invoicePage.tableDimensions}</th>
                <th className="py-3 px-3 font-black w-32 text-left">{pageText.order.invoicePage.tableUnitPrice}</th>
                <th className="py-3 px-3 font-black w-40 text-left">{pageText.order.invoicePage.tableTotalPrice}</th>
              </tr>
            </thead>
            <tbody className="text-slate-800">
              <tr className="border-b border-slate-200">
                <td className="py-4 px-3 font-bold">1</td>
                <td className="py-4 px-3 font-semibold">{pageText.order.invoicePage.printOrderDescription}</td>
                <td className="py-4 px-3 font-medium">1</td>
                <td className="py-4 px-3 text-slate-400 font-medium">N/A</td>
                <td className="py-4 px-3 dir-ltr text-left font-medium">{formatCurrency(invoice?.items_amount)}</td>
                <td className="py-4 px-3 dir-ltr text-left font-bold">{formatCurrency(invoice?.items_amount)}</td>
              </tr>
              {(invoice?.services_amount > 0 || invoice?.tax_amount > 0) && (
                <tr className="border-b border-slate-200 bg-slate-50/80">
                  <td className="py-3 px-3"></td>
                  <td colSpan="4" className="py-3 px-3 text-slate-600 font-medium">{pageText.order.invoicePage.taxAndServices}</td>
                  <td className="py-3 px-3 dir-ltr text-left font-bold">{formatCurrency((invoice?.services_amount || 0) + (invoice?.tax_amount || 0))}</td>
                </tr>
              )}
              <tr className="border-b-4 border-neutral bg-slate-50/30">
                <td colSpan="5" className="py-4 px-3 text-left font-black text-slate-800 text-lg">{pageText.order.invoicePage.totalAmountsLabel}</td>
                <td className="py-4 px-3 font-black dir-ltr text-left text-slate-800 text-lg">{formatCurrency(invoice?.final_amount)} <span className="text-sm font-medium text-slate-500">{globalText.currency}</span></td>
              </tr>
            </tbody>
          </table>
          
          {/* بخش توضیحات */}
          <div className="mt-6 text-sm bg-slate-50/50 py-3 px-4 rounded-xl border border-slate-100 print:border-none print:bg-transparent">
            <p className="text-slate-800 font-medium leading-relaxed">
              <span className="font-black text-primary">{pageText.order.invoicePage.noticeLabel}</span> {pageText.order.invoicePage.noticeText}
            </p>
          </div>
        </div>

        {/* محافظت از شکسته شدن صفحه (جادوی اصلی اینجاست)
          کلاس print:break-inside-avoid نمیذاره این دایو وسطش دو تیکه بشه
        */}
        <div className="print:break-inside-avoid mt-auto pt-16 shrink-0 relative">
          
          {/* بخش پایینی: مهر و امضا + مبالغ نهایی */}
          <div className="px-12 relative flex justify-between items-end mb-6">
            {/* خط زرد جداکننده */}
            <div className="absolute bottom-16 left-12 right-12 h-[3px] bg-neutral print:bg-neutral z-0"></div>

            {/* مهر و امضا */}
            <div className="z-10 bg-white print:bg-white px-8 text-center pb-2">
              <div className="w-24 h-24 bg-secondary text-secondary-content rotate-45 mx-auto mb-6 flex items-center justify-center border-4 border-white shadow-sm print:border-2">
                <span className="-rotate-45 text-xs font-black text-center leading-relaxed">{pageText.order.invoicePage.stampAndSignature}<br/>Printoo24</span>
              </div>
              <p className="font-black text-slate-800 text-sm">{pageText.order.invoicePage.stampEnglish}</p>
            </div>

            {/* خلاصه مبالغ */}
            <div className="z-10 bg-white print:bg-white px-6 text-base w-80 space-y-3 pb-2">
              <div className="flex justify-between items-center bg-slate-50 p-2 rounded-lg">
                <span className="font-black text-red-500 text-lg">{pageText.order.invoicePage.finalTotalLabel}</span>
                <span className="font-black text-red-500 text-xl dir-ltr">{formatCurrency(invoice?.final_amount)} <span className="text-sm">{globalText.currency}</span></span>
              </div>
              <div className="flex justify-between items-center px-2">
                <span className="font-bold text-slate-700">{pageText.order.invoicePage.paidLabel}</span>
                <span className="font-bold text-slate-800 text-lg dir-ltr">{formatCurrency(invoice?.paid_amount)} <span className="text-sm text-slate-500">{globalText.currency}</span></span>
              </div>
              <div className="flex justify-between items-center px-2">
                <span className="font-bold text-slate-700">{pageText.order.invoicePage.remainingLabel}</span>
                <span className="font-black text-slate-900 text-lg dir-ltr">{formatCurrency(Math.max(0, invoice?.remaining_amount || 0))} <span className="text-sm text-slate-500">{globalText.currency}</span></span>
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

export default InvoicePage;