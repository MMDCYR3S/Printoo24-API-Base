import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, AlertCircle } from 'lucide-react';
import { profileService } from '../../services/profileService';

const formatCurrency = (val) => new Intl.NumberFormat('fa-IQ').format(val);

const QuotationPage = () => {
  const { id } = useParams();

  const { data: quotation, isLoading, isError } = useQuery({
    queryKey: ['quotation', id],
    queryFn: () => profileService.getQuotationByOrder(id),
    retry: 1,
  });

  const handlePrint = () => {
    window.print();
  };

  if (isLoading) return <div className="flex justify-center py-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  
  if (isError || !quotation) return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <AlertCircle size={48} className="text-slate-300" />
      <p className="text-slate-500 font-bold">پیش‌فاکتوری برای این سفارش یافت نشد.</p>
      <Link to={`/profile/orders/${id}`} className="btn btn-outline">بازگشت به سفارش</Link>
    </div>
  );

  return (
    <div className="bg-slate-100 min-h-screen py-8">
      
      {/* دکمه‌های کنترلی - خارج از ناحیه چاپ */}
      <div className="max-w-[210mm] mx-auto mb-6 flex justify-between items-center px-4 no-print">
        <Link to={`/profile/orders/${id}`} className="btn btn-ghost bg-white shadow-sm border border-slate-200">
          <ChevronRight size={18} /> بازگشت
        </Link>
        <button onClick={handlePrint} className="btn btn-primary px-8">
          <Printer size={18} /> چاپ رسمی (A4)
        </button>
      </div>

      {/* ناحیه مخصوص چاپ */}
      <div id="printable-area" className="max-w-[210mm] min-h-[297mm] mx-auto bg-white p-[15mm] shadow-xl border border-gray-300 text-black">
        
        {/* استایل‌های اجباری برای خنثی کردن Layout سایت هنگام پرینت */}
        <style dangerouslySetInnerHTML={{__html: `
          @media print {
            /* پنهان کردن کل اجزای سایت (هدر، فوتر، واتساپ و...) */
            body * {
              visibility: hidden;
            }
            /* نمایش اختصاصی فقط برای فاکتور ما */
            #printable-area, #printable-area * {
              visibility: visible;
            }
            #printable-area {
              position: absolute;
              left: 0;
              top: 0;
              width: 210mm;
              margin: 0 !important;
              padding: 10mm !important;
              border: none !important;
              box-shadow: none !important;
            }
            .no-print {
              display: none !important;
            }
            @page {
              size: A4;
              margin: 0;
            }
            /* جلوگیری از شکستن جدول در صفحات */
            table { page-break-inside:auto; }
            tr    { page-break-inside:avoid; page-break-after:auto; }
          }
        `}} />

        {/* --- شروع طراحی رسمی فاکتور --- */}
        <div className="w-full text-sm">
          
          {/* هدر رسمی فاکتور */}
          <div className="flex justify-between items-start mb-6 border-b-2 border-black pb-4">
            <div className="w-1/3 text-right">
              {/* جایگاه لوگو یا اطلاعات شرکت */}
              <h2 className="font-black text-lg">چاپخانه Printoo24</h2>
              <p className="text-xs mt-1">ارائه دهنده خدمات چاپ و تبلیغات</p>
            </div>
            
            <div className="w-1/3 text-center">
              <h1 className="text-2xl font-black">پیش‌فاکتور</h1>
            </div>
            
            <div className="w-1/3 text-left">
              <table className="w-full text-xs float-left max-w-[150px]">
                <tbody>
                  <tr>
                    <td className="text-right py-1">شماره:</td>
                    <td className="font-bold dir-ltr py-1">{quotation.quotation_number}</td>
                  </tr>
                  <tr>
                    <td className="text-right py-1">تاریخ:</td>
                    <td className="font-bold py-1">{new Date(quotation.created_at).toLocaleDateString('fa-IR')}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* باکس مشخصات خریدار */}
          <div className="border border-black rounded-sm mb-6">
            <div className="bg-gray-100 border-b border-black font-bold p-2 text-center text-xs">
              مشخصات خریدار
            </div>
            <div className="p-3">
              <span className="text-xs">نام شخص حقیقی / حقوقی: </span>
              <span className="font-bold">{quotation.customer_name}</span>
            </div>
          </div>

          {/* جدول اقلام (با خطوط کاملا مشخص و اداری) */}
          <table className="w-full border-collapse border border-black mb-6 text-xs text-center">
            <thead className="bg-gray-100">
              <tr>
                <th className="border border-black p-2 w-12">ردیف</th>
                <th className="border border-black p-2 text-right">شرح کالا / خدمات</th>
                <th className="border border-black p-2 w-20">تعداد</th>
                <th className="border border-black p-2 w-32">مبلغ واحد (IQD)</th>
                <th className="border border-black p-2 w-32">مبلغ کل (IQD)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="border border-black p-3">۱</td>
                <td className="border border-black p-3 text-right">
                  <span className="font-bold block mb-1">{quotation.product_name}</span>
                  {quotation.product_snapshot?.meta?.size_info && (
                    <span className="text-[10px] text-gray-600 ml-2">
                      ابعاد: {quotation.product_snapshot.meta.size_info.size_name}
                    </span>
                  )}
                  {quotation.product_snapshot?.options?.map((opt, idx) => (
                    <span key={idx} className="text-[10px] text-gray-600 ml-2 block mt-1">
                      - {opt.option_label}: {opt.value.label}
                    </span>
                  ))}
                </td>
                <td className="border border-black p-3 font-bold">{quotation.quantity}</td>
                {/* محاسبه قیمت واحد (قیمت کل تقسیم بر تعداد - بر اساس دیتای شما) */}
                <td className="border border-black p-3 dir-ltr">
                  {formatCurrency(quotation.total_price / quotation.quantity)}
                </td>
                <td className="border border-black p-3 font-bold dir-ltr">
                  {formatCurrency(quotation.total_price)}
                </td>
              </tr>
              {/* ردیف‌های خالی برای پر کردن فرم فاکتور در صورت نیاز (انتخابی) */}
              <tr>
                <td className="border border-black p-4"></td><td className="border border-black p-4"></td>
                <td className="border border-black p-4"></td><td className="border border-black p-4"></td>
                <td className="border border-black p-4"></td>
              </tr>
            </tbody>
            {/* جمع فاکتور */}
            <tfoot>
              <tr>
                <td colSpan="4" className="border border-black p-2 text-left font-bold">جمع کل قابل پرداخت:</td>
                <td className="border border-black p-2 font-black text-sm dir-ltr bg-gray-50">
                  {formatCurrency(quotation.total_price)}
                </td>
              </tr>
            </tfoot>
          </table>

          {/* فوتر فاکتور (توضیحات و امضا) */}
          <div className="flex border border-black rounded-sm h-32 text-xs">
            <div className="w-2/3 p-3 border-l border-black">
              <strong className="block mb-2">توضیحات:</strong>
              <p className="text-gray-600 leading-relaxed">
                ۱. این پیش‌فاکتور صرفاً جهت اطلاع از برآورد هزینه‌ها صادر شده است. <br/>
                ۲. اعتبار قیمت‌های مندرج تا پایان زمان اعلام شده معتبر می‌باشد.
              </p>
            </div>
            <div className="w-1/3 flex flex-col justify-between p-3">
              <span className="font-bold text-center block">مهر و امضای فروشنده</span>
              {/* جای خالی برای امضا */}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default QuotationPage;