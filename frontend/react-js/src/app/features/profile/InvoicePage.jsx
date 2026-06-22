import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Printer, ChevronRight, Receipt, Phone, MapPin, Facebook, Instagram } from 'lucide-react';
import { profileService } from '../../services/profileService';
import { formatCurrency } from '../../utils/formatters';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const InvoicePage = () => {
  const { id } = useParams();
  const [scale, setScale] = useState(1);

  const { data: invoice, isLoading, isError, error } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => profileService.getInvoiceByOrder(id),
    retry: false,
  });

  useEffect(() => {
    const updateScale = () => {
      const invoiceWidthPx = 793.7;
      const padding = 16;
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
          {pageText.order.invoicePage.backToOrder}
        </Link>
        <button
          onClick={handlePrint}
          className="btn btn-neutral rounded-xl px-7 gap-2 shadow-md"
        >
          <Printer size={16} />
          {pageText.order.invoicePage.printInvoice}
        </button>
      </div>

      {/* ═══════════════════════════════════════
          SCALER WRAPPER
      ═══════════════════════════════════════ */}
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
            {/* top strip: logo left / phones right */}
            <div className="flex items-center justify-between px-8 pt-5 pb-4">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-primary rounded-2xl flex items-center justify-center shadow-md shadow-black/20">
                  <span className="text-primary-content font-black text-base tracking-tight leading-none">P24</span>
                </div>
                <div>
                  <p className="text-neutral-content font-black text-xl tracking-tight leading-none">Printoo24</p>
                  <p className="text-neutral-content/50 text-xs mt-0.5 font-medium">{pageText.order.invoicePage.address}</p>
                </div>
              </div>

              {/* Phones */}
              <div className="text-right space-y-1.5">
                <div className="flex items-center justify-end gap-2 text-neutral-content/80 text-sm font-semibold " dir='ltr'>
                  <Phone size={14} className="text-primary shrink-0" />
                  <span>0776 2278 666</span>
                </div>
              </div>
            </div>

            {/* tagline banner */}
            <div className="bg-black/10 px-8 py-2 flex items-center justify-center">
              <p className="text-neutral-content/70 text-xs font-medium tracking-wide">
                {pageText.order.invoicePage.brandName}
              </p>
            </div>
          </div>

          {/* ── INVOICE TITLE + META ── */}
          <div className="px-8 py-6 flex items-start justify-between border-b border-slate-100 shrink-0">
            {/* Title block */}
            <div>
              <h1 className="text-red-500 font-light tracking-widest text-4xl leading-none" style={{fontFamily: 'Georgia, serif'}}>
                Invoice
              </h1>
              <p className="text-slate-400 text-xs mt-1.5 font-medium tracking-wide uppercase">
                {pageText.order.invoicePage.invoiceTitle}
              </p>
              <p className="text-slate-300 text-xs mt-0.5">Page 1 of 1</p>
            </div>

            {/* Meta card */}
            <div className="bg-slate-50 rounded-2xl border border-slate-100 px-5 py-4 space-y-2.5 min-w-[200px] text-sm">
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">{pageText.order.invoicePage.issuedFor}</span>
                <span className="font-bold text-slate-700 text-right">{invoice?.customer_name || pageText.order.invoicePage.defaultCustomer}</span>
              </div>
              {invoice?.customer_phone && (
                <div className="flex gap-4 justify-between items-center">
                  <span className="text-slate-400 font-medium shrink-0">{pageText.order.invoicePage.contactNumber}</span>
                  <span className="font-semibold text-slate-600 dir-ltr">{invoice.customer_phone}</span>
                </div>
              )}
              <div className="h-px bg-slate-200" />
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">{pageText.order.invoicePage.invoiceNumber}</span>
                <span className="font-black text-red-500 dir-ltr text-base">{invoice?.invoice_number}</span>
              </div>
              <div className="flex gap-4 justify-between items-center">
                <span className="text-slate-400 font-medium shrink-0">{pageText.order.invoicePage.issueDate}</span>
                <span className="font-semibold text-red-400 dir-ltr">
                  {new Date(invoice?.issued_at || Date.now()).toLocaleDateString('en-GB').replace(/\//g, '.')}
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
                    ID
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-right">
                    {pageText.order.invoicePage.tableDescription}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-center w-20">
                    {pageText.order.invoicePage.tableQuantity}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-center w-20">
                    {pageText.order.invoicePage.tableDimensions}
                  </th>
                  <th className="pb-3 px-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-center w-32">
                    {pageText.order.invoicePage.tableUnitPrice}
                  </th>
                  <th className="pb-3 pl-3 text-slate-400 font-semibold text-xs tracking-widest uppercase border-b-2 border-neutral text-left w-36">
                    {pageText.order.invoicePage.tableTotalPrice}
                  </th>
                </tr>
              </thead>
              <tbody>
                {/* Main row */}
                <tr className="border-b border-slate-100 group">
                  <td className="py-4 pr-3 text-slate-300 font-medium">1</td>
                  <td className="py-4 px-3 font-semibold text-slate-700">
                    {pageText.order.invoicePage.printOrderDescription}
                  </td>
                  <td className="py-4 px-3 text-center text-slate-300">—</td>
                  <td className="py-4 px-3 text-center text-slate-300">—</td>
                  <td className="py-4 px-3 text-center text-slate-300">—</td>
                  <td className="py-4 pl-3 dir-ltr text-left font-bold text-slate-800">
                    {formatCurrency(invoice?.items_amount)}
                    <span className="text-slate-400 text-xs font-normal ml-1">IQD</span>
                  </td>
                </tr>

                {/* Tax/services */}
                {(invoice?.services_amount > 0 || invoice?.tax_amount > 0) && (
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <td className="py-3 pr-3 text-slate-300">2</td>
                    <td colSpan={4} className="py-3 px-3 text-slate-500 font-medium">
                      {pageText.order.invoicePage.taxAndServices}
                    </td>
                    <td className="py-3 pl-3 dir-ltr text-left font-bold text-slate-700">
                      {formatCurrency((invoice?.services_amount || 0) + (invoice?.tax_amount || 0))}
                      <span className="text-slate-400 text-xs font-normal ml-1">IQD</span>
                    </td>
                  </tr>
                )}

                {/* spacer */}
                <tr>
                  <td colSpan={6} className="py-6"></td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* ── NOTICE ── */}
          <div className="px-8 pb-6 shrink-0">
            <div className="border-r-4 border-primary bg-slate-50 rounded-xl px-4 py-3 print:bg-transparent">
              <p className="text-slate-500 text-xs leading-relaxed">
                <span className="font-bold text-slate-700">{pageText.order.invoicePage.noticeLabel}</span>{' '}
                {pageText.order.invoicePage.noticeText}
              </p>
            </div>
          </div>

          {/* ── TOTALS + STAMP ── */}
          <div className="mt-auto print:break-inside-avoid shrink-0">

            {/* Summary numbers */}
            <div className="px-8 pt-5 pb-6 border-t-2 border-slate-100">
              <div className="flex justify-between items-end gap-8">

                {/* Stamp */}
                <div className="flex flex-col items-center gap-2">
                  <div className="w-20 h-20 rounded-full border-2 border-dashed border-neutral flex items-center justify-center">
                    <div className="text-center">
                      <p className="text-neutral font-black text-xs leading-tight">P24</p>
                      <p className="text-neutral/60 text-[9px] leading-tight mt-0.5 font-semibold">STAMP</p>
                    </div>
                  </div>
                  <p className="text-slate-400 text-xs font-medium">{pageText.order.invoicePage.stampEnglish}</p>
                </div>

                {/* Amounts */}
                <div className="flex-1 max-w-xs space-y-2">
                  {/* Total */}
                  <div className="bg-neutral/5 rounded-xl px-4 py-3 flex justify-between items-center border border-neutral/10">
                    <span className="font-black text-slate-800 text-sm">{pageText.order.invoicePage.finalTotalLabel}</span>
                    <span className="font-black text-red-500 text-lg dir-ltr">
                      {formatCurrency(invoice?.final_amount)}
                      <span className="text-xs font-medium text-slate-400 ml-1">IQD</span>
                    </span>
                  </div>

                  {/* Paid */}
                  <div className="flex justify-between items-center px-2 py-1">
                    <span className="text-slate-500 text-sm font-semibold">{pageText.order.invoicePage.paidLabel}</span>
                    <span className="font-semibold text-slate-600 text-sm dir-ltr">
                      {formatCurrency(invoice?.paid_amount)}
                      <span className="text-xs font-normal text-slate-400 ml-1">IQD</span>
                    </span>
                  </div>

                  {/* Remaining */}
                  <div className="flex justify-between items-center px-2 py-1 border-t border-dashed border-slate-200 pt-2">
                    <span className="text-slate-500 text-sm font-semibold">{pageText.order.invoicePage.remainingLabel}</span>
                    <span className="font-black text-slate-900 text-sm dir-ltr">
                      {formatCurrency(Math.max(0, invoice?.remaining_amount || 0))}
                      <span className="text-xs font-normal text-slate-400 ml-1">IQD</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* ── FOOTER BAR ── */}
            <div className="bg-neutral px-8 py-4 flex items-center justify-center gap-3">
              <Facebook size={18} className="text-neutral-content/60" />
              <Instagram size={18} className="text-neutral-content/60" />
              <span className="text-neutral-content font-black tracking-[0.2em] text-sm uppercase mx-2">
                Printoo24
              </span>
              <Instagram size={18} className="text-neutral-content/60 opacity-0" />
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default InvoicePage;