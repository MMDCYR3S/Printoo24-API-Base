// src/app/features/shop/components/AdminOrderPanel.jsx
import React, { useState, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { ShieldCheck, User, MapPin, Loader2, Send, AlertCircle } from 'lucide-react';

import { shopService } from '../../../services/shopService';

/**
 * AdminOrderPanel
 * ----------------
 * پنل مخصوص ادمین برای ثبت سفارش دستی به‌نام یک مشتری.
 *
 * فقط زمانی باید رندر شود که کاربر فعلی is_superuser === true باشد
 * (تشخیص در ProductDetailPage انجام می‌شود).
 *
 * Props:
 *  - productData       : داده‌ی کامل محصول (از getProductDetail)
 *  - getSubmitPayload  : تابعی که { product_id, options } برمی‌گرداند (از useProductCalculator)
 *  - pricing           : وضعیت قیمت محاسبه‌شده ({ totalPrice, isCalculating, error })
 *  - hasPrice          : آیا محصول قیمت دارد؟ (data.has_price)
 */
const AdminOrderPanel = ({ productData, getSubmitPayload, pricing, hasPrice }) => {
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [selectedAddressId, setSelectedAddressId] = useState('');

  // ── واکشی لیست مشتریان ──────────────────────────────────────────────────
  const {
    data: customers = [],
    isLoading: customersLoading,
    error: customersError,
  } = useQuery({
    queryKey: ['dashboard-customers'],
    queryFn: shopService.getDashboardCustomers,
    staleTime: 60_000, // یک دقیقه کش
  });

  // مشتری انتخاب‌شده (برای دسترسی به addresses)
  const selectedCustomer = useMemo(
    () => customers.find((c) => c.id === Number(selectedCustomerId)) || null,
    [customers, selectedCustomerId]
  );

  const addresses = selectedCustomer?.addresses || [];

  // ── هندلرها ────────────────────────────────────────────────────────────
  const handleCustomerChange = (e) => {
    setSelectedCustomerId(e.target.value);
    setSelectedAddressId(''); // ری‌ست آدرس هنگام تغییر مشتری
  };

  const handleAddressChange = (e) => {
    setSelectedAddressId(e.target.value);
  };

  // ── Mutation ثبت سفارش دستی ────────────────────────────────────────────
  const createOrderMutation = useMutation({
    mutationFn: shopService.createManualOrder,
    onSuccess: (response) => {
      toast.success('سفارش با موفقیت برای مشتری ثبت شد');
      // اختیاری: در صورت نیاز به انتقال به صفحه‌ی جزئیات سفارش
      // const orderId = response?.id;
      // if (orderId) navigate(`/dashboard/orders/${orderId}`);

      // ری‌ست انتخاب‌ها پس از ثبت موفق
      setSelectedCustomerId('');
      setSelectedAddressId('');
    },
    onError: (err) => {
      console.error('Manual Order Error:', err?.response?.data);
      const data = err?.response?.data || {};
      // پشتیبانی از چند فرمت خطای متداول در DRF
      const msg =
        data.error ||
        data.detail ||
        (typeof data === 'string' ? data : null) ||
        'خطا در ثبت سفارش دستی. لطفاً دوباره تلاش کنید.';
      toast.error(msg);
    },
  });

  // ── آماده‌سازی پیلود و سابمیت ─────────────────────────────────────────
  const handleSubmitManualOrder = () => {
    // اعتبارسنجی مشتری
    if (!selectedCustomerId) {
      toast.error('لطفاً مشتری را انتخاب کنید');
      return;
    }
    // اعتبارسنجی آدرس
    if (!selectedAddressId) {
      toast.error('لطفاً آدرس را انتخاب کنید');
      return;
    }
    // اعتبارسنجی فیلدهای اجباری محصول
    const payloadInfo = getSubmitPayload ? getSubmitPayload() : {};
    if (!payloadInfo?.product_id) {
      toast.error('اطلاعات محصول ناقص است');
      return;
    }

    // تبدیل selections (آبجکت) به آرایه‌ی {field_id, choice_id}
    // payloadInfo.options معمولاً به‌صورت { [fieldId]: choiceId | [choiceId,...] } است
    const optionsObj = payloadInfo.options || {};
    const selectedOptionsArr = [];

    Object.entries(optionsObj).forEach(([fieldId, value]) => {
      if (value === null || value === undefined || value === '') return;
      // پشتیبانی از multi_select که value آرایه است
      if (Array.isArray(value)) {
        value.forEach((v) => {
          if (v !== null && v !== undefined && v !== '') {
            selectedOptionsArr.push({
              field_id: Number(fieldId),
              choice_id: Number(v),
            });
          }
        });
      } else {
        selectedOptionsArr.push({
          field_id: Number(fieldId),
          choice_id: Number(value),
        });
      }
    });

    // ⚠️ توجه: company_name هرگز در پیلود قرار نمی‌گیرد
    const payload = {
      user_id: Number(selectedCustomerId),
      address_id: Number(selectedAddressId),
      type: String(productData?.type ?? '1'), // پیش‌فرض "1" در صورت نبود فیلد
      product_id: Number(payloadInfo.product_id),
      has_design: Boolean(productData?.has_design ?? false),
      selected_options: selectedOptionsArr,
    };

    createOrderMutation.mutate(payload);
  };

  // ── وضعیت دکمه ─────────────────────────────────────────────────────────
  const isSubmitDisabled =
    createOrderMutation.isLoading ||
    !selectedCustomerId ||
    !selectedAddressId ||
    !hasPrice ||
    pricing?.isCalculating ||
    !!pricing?.error;

  // ── رندر ───────────────────────────────────────────────────────────────
  return (
    <div className="bg-white rounded-3xl shadow-xl shadow-amber-200/40 border-2 border-amber-200 overflow-hidden">
      {/* هدر پنل */}
      <div className="p-4 bg-gradient-to-l from-amber-500 to-orange-500 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck size={18} />
          <h3 className="font-bold text-sm">ثبت سفارش دستی</h3>
        </div>
        <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-bold">
          پنل مدیریت
        </span>
      </div>

      {/* بدنه پنل */}
      <div className="p-4 md:p-5 space-y-4">
        {/* خطای واکشی مشتریان */}
        {customersError && (
          <div className="flex items-start gap-2 text-rose-600 text-xs font-bold bg-rose-50 p-3 rounded-xl border border-rose-100">
            <AlertCircle size={14} className="shrink-0 mt-0.5" />
            <span className="leading-relaxed">
              خطا در بارگذاری لیست مشتریان. لطفاً صفحه را تازه‌سازی کنید.
            </span>
          </div>
        )}

        {/* انتخاب مشتری */}
        <div>
          <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1.5">
            <User size={13} className="text-amber-500" />
            انتخاب مشتری
          </label>
          <select
            value={selectedCustomerId}
            onChange={handleCustomerChange}
            disabled={customersLoading}
            className="w-full px-3 py-2.5 rounded-xl border-2 border-slate-100 bg-slate-50 text-sm font-medium text-slate-800 focus:border-amber-400 focus:bg-white outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option value="">
              {customersLoading ? 'در حال بارگذاری...' : '— انتخاب کنید —'}
            </option>
            {customers.map((c) => {
              const name = (c.full_name || '').trim() || 'بی‌نام';
              const company = (c.company || '').trim();
              const label = company
                ? `${name} • ${c.phone_number} • ${company}`
                : `${name} • ${c.phone_number}`;
              return (
                <option key={c.id} value={c.id}>
                  {label}
                </option>
              );
            })}
          </select>
        </div>

        {/* انتخاب آدرس — فقط وقتی مشتری انتخاب شده باشد */}
        {selectedCustomer && (
          <div className="animate-in fade-in slide-in-from-top-2 duration-300">
            <label className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-1.5">
              <MapPin size={13} className="text-amber-500" />
              انتخاب آدرس
            </label>
            {addresses.length === 0 ? (
              <div className="flex items-start gap-2 text-rose-600 text-xs font-bold bg-rose-50 p-3 rounded-xl border border-rose-100">
                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                <span className="leading-relaxed">
                  این مشتری هیچ آدرس ثبت‌شده‌ای ندارد. ابتدا از پنل کاربری برایش آدرس اضافه کنید.
                </span>
              </div>
            ) : (
              <select
                value={selectedAddressId}
                onChange={handleAddressChange}
                className="w-full px-3 py-2.5 rounded-xl border-2 border-slate-100 bg-slate-50 text-sm font-medium text-slate-800 focus:border-amber-400 focus:bg-white outline-none transition-all"
              >
                <option value="">— انتخاب کنید —</option>
                {addresses.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.province_name} - {a.city_name} - {a.address}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        {/* خلاصه‌ی انتخاب فعلی */}
        {selectedCustomer && selectedAddressId && (
          <div className="text-xs text-slate-500 bg-amber-50/50 border border-amber-100 rounded-xl p-3 space-y-1">
            <div className="font-bold text-slate-700">
              سفارش برای: {(selectedCustomer.full_name || '').trim() || selectedCustomer.phone_number}
            </div>
            <div className="text-slate-500">
              مبلغ نهایی:{' '}
              <span className="font-bold text-emerald-600">
                {Number(pricing?.totalPrice || 0).toLocaleString()}
              </span>{' '}
              IQD
            </div>
          </div>
        )}

        {/* دکمه ثبت سفارش */}
        <button
          onClick={handleSubmitManualOrder}
          disabled={isSubmitDisabled}
          className="w-full h-12 rounded-xl text-sm font-bold bg-gradient-to-l from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/25 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:shadow-xl hover:shadow-amber-500/30 transition-all active:scale-[0.98]"
        >
          {createOrderMutation.isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              در حال ثبت سفارش...
            </>
          ) : (
            <>
              <Send size={16} />
              ثبت سفارش برای مشتری
            </>
          )}
        </button>

        {/* راهنما */}
        <p className="text-[11px] text-slate-400 leading-relaxed">
          توجه: این سفارش به‌نام مشتری انتخاب‌شده ثبت می‌شود. ابتدا گزینه‌های محصول را در بالای صفحه انتخاب کنید، سپس مشتری و آدرس را مشخص نمایید.
        </p>
      </div>
    </div>
  );
};

export default AdminOrderPanel;
