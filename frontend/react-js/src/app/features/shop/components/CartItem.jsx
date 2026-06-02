import React from 'react';
import {
  Trash2,
  UploadCloud,
  CheckCircle,
  Plus,
  ImageOff,
  FileText,
  Hash,
} from 'lucide-react';
import { Link } from 'react-router-dom';

import pageText from '../../../lang/pages.json';
import globalText from '../../../lang/global.json';

const CartItem = ({ item, onDelete, isDeleting }) => {
  const specs = item.items || {};
  const uploads = item.uploads || [];
  const hasUpload = uploads.length > 0;
  const productImage = item.product?.image;
  const productName = item.product?.name || item.name;

  return (
    <div
      className={`
        bg-white rounded-2xl
        ring-1 ring-black/[0.05]
        hover:ring-black/[0.08]
        hover:shadow-md hover:shadow-black/[0.04]
        transition-all duration-300
        overflow-hidden
        ${isDeleting ? 'opacity-50 pointer-events-none' : ''}
      `}
    >
      <div className="flex flex-col sm:flex-row">

        {/* ── تصویر ── */}
        <div className="shrink-0 sm:w-36 md:w-40">
          <div className="aspect-[4/3] sm:aspect-auto sm:h-full bg-slate-100 overflow-hidden">
            {productImage ? (
              <img
                src={productImage}
                alt={productName}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full min-h-[120px] flex flex-col items-center justify-center gap-1.5 text-slate-300">
                <ImageOff size={28} strokeWidth={1.3} />
              </div>
            )}
          </div>
        </div>

        {/* ── محتوا ── */}
        <div className="flex-1 flex flex-col p-4 sm:p-5 min-w-0">

          {/* ردیف بالا: نام + حذف موبایل */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="min-w-0">
              <h3 className="text-[15px] font-bold text-slate-800 leading-snug line-clamp-1 mb-1">
                {productName}
              </h3>
              <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-medium">
                <Hash size={11} />
                <span className="dir-ltr">{item.product?.slug}</span>
              </div>
            </div>
            {/* دکمه حذف موبایل */}
            <button
              onClick={() => onDelete(item.id)}
              disabled={isDeleting}
              className="
                sm:hidden shrink-0
                w-8 h-8 flex items-center justify-center
                rounded-lg text-slate-300
                hover:text-red-500 hover:bg-red-50
                transition-colors duration-200
              "
            >
              <Trash2 size={16} />
            </button>
          </div>

          {/* مشخصات */}
{/* مشخصات */}
<div className="
  bg-slate-50/80 rounded-xl p-3.5
  flex flex-col gap-2 text-[13px]
  mb-3
">
  {(item.selections || []).map((sel, idx) => (
    <div key={idx} className="flex items-center justify-between py-0.5">
      <span className="text-slate-500">{sel.field_title}</span>
      <span className="font-semibold text-slate-700">{sel.value}</span>
    </div>
  ))}

  <div className="flex items-center justify-between py-0.5 border-t border-slate-100 mt-1 pt-2">
    <span className="text-slate-500">تعداد</span>
    <span className="font-semibold text-slate-700">{item.quantity.toLocaleString()}</span>
  </div>
</div>

          {/* وضعیت فایل */}
          <div className="flex flex-wrap items-center gap-2 mt-auto">
            {hasUpload ? (
              <>
                <div className="
                  inline-flex items-center gap-1.5
                  text-[11px] font-bold
                  text-emerald-600 bg-emerald-50
                  px-2.5 py-1.5 rounded-lg
                  ring-1 ring-emerald-100/60
                ">
                  <CheckCircle size={13} />
                  {pageText.cart.cartItem.filesUploaded.replace('{{count}}', uploads.length)}
                </div>
                <Link
                  to={`/cart/upload/${item.id}`}
                  className="
                    inline-flex items-center gap-1
                    text-[11px] font-bold text-blue-500
                    px-2.5 py-1.5 rounded-lg
                    hover:bg-blue-50 transition-colors
                  "
                >
                  <Plus size={13} />
                  {pageText.cart.cartItem.manageFiles}
                </Link>
              </>
            ) : (
              <Link
                to={`/cart/upload/${item.id}`}
                className="
                  inline-flex items-center gap-2
                  text-[11px] font-bold text-slate-500
                  bg-slate-100/80 hover:bg-slate-200/80
                  px-3 py-2 rounded-lg
                  ring-1 ring-black/[0.04]
                  transition-colors duration-200
                "
              >
                <UploadCloud size={14} />
                {pageText.cart.cartItem.uploadDesignOptional}
              </Link>
            )}
          </div>
        </div>

        {/* ── قیمت + حذف (دسکتاپ) ── */}
        <div className="
          hidden sm:flex flex-col justify-between items-end
          p-5 pr-0 mr-5
          border-r border-slate-100
          min-w-[130px]
        ">
          <div className="text-left">
            <span className="block text-[10px] text-slate-400 font-medium mb-1">
              {pageText.cart.cartItem.itemTotalPriceLabel}
            </span>
            <div className="flex items-baseline gap-1">
              <span className="text-xl font-extrabold text-slate-800 tabular-nums tracking-tight">
                {parseFloat(item.price).toLocaleString()}
              </span>
              <span className="text-[10px] font-bold text-slate-400">
                {pageText.cart.cartItem.currency}
              </span>
            </div>
          </div>

          <button
            onClick={() => onDelete(item.id)}
            disabled={isDeleting}
            className="
              flex items-center gap-1.5
              text-xs font-medium
              text-slate-400 hover:text-red-500
              hover:bg-red-50
              px-2.5 py-1.5 rounded-lg
              transition-all duration-200
              mt-3
            "
          >
            <Trash2 size={14} />
            {pageText.cart.cartItem.deleteItemBtn}
          </button>
        </div>

        {/* قیمت موبایل */}
        <div className="
          sm:hidden flex items-center justify-between
          px-4 py-3
          border-t border-slate-100
          bg-slate-50/50
        ">
          <span className="text-xs text-slate-400 font-medium">
            {pageText.cart.cartItem.itemTotalPriceLabel}
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-lg font-extrabold text-slate-800 tabular-nums">
              {parseFloat(item.price).toLocaleString()}
            </span>
            <span className="text-[10px] font-bold text-slate-400">
              {pageText.cart.cartItem.currency}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ─────────────────────────────────────────────
   ردیف مشخصات
   ───────────────────────────────────────────── */
const SpecRow = ({ label, value, highlight = false, mono = false }) => (
  <div className={`
    flex items-center justify-between py-0.5
    ${highlight ? 'text-blue-600' : ''}
  `}>
    <span className={`${highlight ? 'opacity-70' : 'text-slate-500'}`}>
      {label}
    </span>
    <span className={`
      font-semibold
      ${highlight ? '' : 'text-slate-700'}
      ${mono ? 'font-mono dir-ltr text-xs' : ''}
    `}>
      {value}
    </span>
  </div>
);

export default CartItem;