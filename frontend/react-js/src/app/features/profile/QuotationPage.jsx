import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, AlertCircle, Phone, MapPin, Instagram } from 'lucide-react';
import { profileService } from '../../services/profileService';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const formatCurrency = (val) => new Intl.NumberFormat('EN').format(val);

const QuotationPage = () => {
  const { id } = useParams();
  const [scale, setScale] = useState(1);

  const { data: quotation, isLoading, isError, error } = useQuery({
    queryKey: ['quotation', id],
    queryFn: () => profileService.getQuotationByOrder(id),
    retry: 1,
  });

  // ── محاسبه scale برای موبایل ──
  useEffect(() => {
    const updateScale = () => {
      const invoiceWidthPx = 793.7; // 210mm در 96 DPI
      const padding = 16;            // فضا برای اینکه به لبه نچسبه
      const available = window.innerWidth - padding;
      if (window.innerWidth < invoiceWidthPx + padding) {
        setScale(available / invoiceWidthPx);
      } else {
        setScale(1);
      }
    };
    updateScale();
    window.addEventListener('resize', updateScale);
    window.addEventListener('orientationchange', updateScale);
    return () => {
      window.removeEventListener('resize', updateScale);
      window.removeEventListener('orientationchange', updateScale);
    };
  }, []);

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
          {error?.response?.data?.detail || "لەوانەیە پێشفاکتەرەکە سڕدرابێتەوە، یان کێشەیەک لە وەرگرتنی زانیارییەکاندا هەبێت."}
        </p>
        <Link to={`/profile/orders/${id}`} className="btn btn-primary rounded-xl px-8 shadow-lg shadow-primary/20 mt-4">
          {pageText.order.quotationPage.backToOrder}
        </Link>
      </div>
    );
  }

  // product_snapshot is an array of selections: [{ field_title, value, ... }]
  const selections = Array.isArray(quotation.product_snapshot) ? quotation.product_snapshot : [];

  return (
    <div className="min-h-screen pb-10 print:pb-0 print:bg-white animate-in fade-in duration-500 bg-base-200 flex flex-col items-center" dir="rtl">

      <style type="text/css" media="print">{`
        @page { size: A4 portrait; margin: 0; }
        body {
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
          background: white !important;
          margin: 0 !important;
          padding: 0 !important;
        }
        body * { visibility: hidden !important; }
        #printable-invoice, #printable-invoice * { visibility: visible !important; }
        #printable-invoice {
          position: absolute !important;
          left: 0 !important; top: 0 !important;
          width: 210mm !important;
          min-height: 297mm !important;
          margin: 0 !important; padding: 0 !important;
          box-shadow: none !important;
          border: none !important;
          background: white !important;
          transform: none !important;
        }
        #invoice-scaler { height: auto !important; overflow: visible !important; }
      `}</style>

      {/* ── Action bar (hidden in print) ── */}
      <div className="w-full max-w-[210mm] pt-7 mb-5 flex justify-between items-center print:hidden px-2 gap-2">
        <Link
          to={`/profile/orders/${id}`}
          className="btn btn-ghost text-base-content/60 hover:bg-base-300 rounded-xl gap-1"
        >
          <ChevronRight size={17} />
          {pageText.order.quotationPage.backBtn}
        </Link>
        <button
          onClick={handlePrint}
          className="btn btn-neutral rounded-xl px-7 gap-2 shadow-md"
        >
          <Printer size={16} />
          {pageText.order.quotationPage.printBtn}
        </button>
      </div>

      {/* ── SCALER WRAPPER ── */}
      <div
        id="invoice-scaler"
        className="w-full flex justify-center print:block"
        style={{
          height: `calc(297mm * ${scale})`,
          overflow: 'hidden',
        }}
      >
        <div
          id="printable-invoice"
          style={{
            transform: `scale(${scale})`,
            transformOrigin: 'top center',
            flexShrink: 0,
          }}
          className="w-[210mm] max-w-none min-h-[297mm] bg-white shadow-2xl shadow-slate-300/30 border border-slate-200 print:border-none flex flex-col overflow-hidden"
        >

          {/* ── HEADER ── */}
          <div className="bg-neutral shrink-0">
            <div className="flex items-center justify-between px-8 pt-5 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center shadow-md shadow-black/20">
                  <span className="text-primary-content font-black text-base tracking-tight leading-none">P24</span>
                </div>
                <div>
                  <p className="text-neutral-content font-black text-xl tracking-tight leading-none">
                    {pageText.order.quotationPage.brandName}
                  </p>
                  <p className="text-neutral-content/50 text-xs mt-0.5 font-medium">
                    {pageText.order.quotationPage.brandSub}
                  </p>
                </div>
              </div>
              <div className="text-right space-y-1.5">
                <div className="flex items-center justify-end gap-2 text-neutral-content/80 text-sm font-semibold dir-ltr">
                  <Phone size={14} className="text-primary shrink-0" />
                  <span dir='ltr'>776 227 8666</span>
                </div>
                <div className="flex items-center justify-end gap-2 text-neutral-content/80 text-sm font-semibold">
                  <MapPin size={14} className="text-primary shrink-0" />
                  <span>{pageText.order.quotationPage.brandSub}</span>
                </div>
              </div>
            </div>
            <div className="bg-black/10 px-8 py-2 flex items-center justify-center">
              <p className="text-neutral-content/70 text-xs font-medium tracking-wide">
                {pageText.order.quotationPage.brandName}
              </p>
            </div>
          </div>

          {/* ── QUOTATION TITLE + META ── */}
          <div className="px-8 py-6 flex items-start justify-between border-b border-slate-100 shrink-0">
            <div>
              <h1 className="text-blue-500 font-light tracking-widest text-4xl leading-none" style={{ fontFamily: 'Georgia, serif' }}>
                Quotation
              </h1>
              <p className="text-slate-400 text-xs mt-1.5 font-medium tracking-wide uppercase">
                {pageText.order.quotationPage.pageTitle}
              </p>
              <p className="text-slate-300 text-xs mt-0.5">Page 1 of 1</p>
            </div>
            <div className="bg-slate-50 rounded-2xl border border-slate-100 px-5 py-4 space-y-2.5 min-w-[200px] text-sm">
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">{pageText.order.quotationPage.customerInfoTitle}:</span>
                <span className="font-bold text-slate-700 text-right">{quotation.customer_name}</span>
              </div>
              <div className="h-px bg-slate-200" />
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">
                  {pageText.order.quotationPage.pageTitle} {pageText.order.quotationPage.numberLabel}
                </span>
                <span className="font-black text-blue-500 dir-ltr text-base">{quotation.quotation_number}</span>
              </div>
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">{pageText.order.quotationPage.dateLabel}</span>
                <span className="font-semibold text-blue-400 dir-ltr">
                  {new Date(quotation.created_at).toLocaleDateString('EN')}
                </span>
              </div>
            </div>
          </div>

          {/* ── TABLE ── */}
          <div className="px-8 pt-6 flex-grow">
            <table className="w-full text-sm text-right border-collapse">
              <thead>
                <tr>
                  <th className="pb-3 pr-3 text-slate-400 font-semibold text-xs tracking-widest uppercase w-10 border-b-2 border-neutral">
                    {pageText.order.quotationPage.tableRow}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-right">
                    {pageText.order.quotationPage.tableDescription}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-center w-20">
                    {pageText.order.quotationPage.tableQuantity}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-center w-32">
                    {pageText.order.quotationPage.tableUnitPrice}
                  </th>
                  <th className="pb-3 pl-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-left w-36">
                    {pageText.order.quotationPage.tableTotalPrice}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-100">
                  <td className="py-4 pr-3 text-slate-300 font-medium">1</td>
                  <td className="py-4 px-3 font-semibold text-slate-700 text-right">

                    {/* نام محصول */}
                    <span className="font-bold block mb-2">{quotation.product_name}</span>

                    {/* گزینه‌های انتخابی کاربر از product_snapshot */}
                    {selections.map((sel, idx) => (
                      <span key={idx} className="text-xs font-medium text-slate-500 flex gap-1 mt-1">
                        <span className="font-bold text-slate-700 shrink-0">{sel.field_title}:</span>
                        <span>{Array.isArray(sel.value) ? sel.value.join('، ') : sel.value}</span>
                      </span>
                    ))}

                  </td>
                  <td className="py-4 px-3 text-center text-slate-700 font-medium">
                    {quotation.quantity}
                  </td>
                  <td className="py-4 px-3 text-center font-medium text-slate-700 dir-ltr">
                    {formatCurrency(quotation.total_price / quotation.quantity)}
                    <span className="text-slate-400 text-xs font-normal ml-1">{globalText.currency}</span>
                  </td>
                  <td className="py-4 pl-3 dir-ltr text-left font-bold text-slate-800">
                    {formatCurrency(quotation.total_price)}
                    <span className="text-slate-400 text-xs font-normal ml-1">{globalText.currency}</span>
                  </td>
                </tr>

                <tr>
                  <td colSpan={5} className="py-6"></td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* ── NOTES ── */}
          <div className="px-8 pb-6 shrink-0">
            <div className="border-r-4 border-primary bg-slate-50 rounded-xl px-4 py-3 print:bg-transparent">
              <p className="text-slate-500 text-xs leading-relaxed">
                <span className="font-bold text-slate-700">{pageText.order.quotationPage.notesTitle}</span>{' '}
                {pageText.order.quotationPage.note1}
                <br />
                {pageText.order.quotationPage.note2}
              </p>
            </div>
          </div>

          {/* ── TOTAL + STAMP ── */}
          <div className="mt-auto print:break-inside-avoid shrink-0">
            <div className="px-8 pt-5 pb-6 border-t-2 border-slate-100">
              <div className="flex justify-between items-end gap-8">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-20 h-20 rounded-full border-2 border-dashed border-neutral flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-neutral font-black text-xs leading-tight">P24</p>
                      <p className="text-neutral/60 text-[9px] leading-tight mt-0.5 font-semibold">STAMP</p>
                    </div>
                  </div>
                  <p className="text-slate-400 text-xs font-medium">{pageText.order.quotationPage.sellerStamp}</p>
                </div>
                <div className="flex-1 max-w-xs space-y-2">
                  <div className="bg-neutral/5 rounded-xl px-4 py-3 flex justify-between items-center border border-neutral/10">
                    <span className="font-black text-slate-800 text-sm">{pageText.order.quotationPage.totalPayable}</span>
                    <span className="font-black text-blue-500 text-lg dir-ltr">
                      {formatCurrency(quotation.total_price)}
                      <span className="text-xs font-medium text-slate-400 ml-1">{globalText.currency}</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* ── FOOTER BAR ── */}
            <div className="bg-neutral px-8 py-4 flex items-center justify-center gap-3">
              <span className="text-neutral-content font-black tracking-[0.2em] text-sm uppercase mx-2">
                printoo24.com
              </span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default QuotationPage;