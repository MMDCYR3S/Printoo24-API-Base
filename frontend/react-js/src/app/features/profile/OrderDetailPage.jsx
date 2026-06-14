import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Download,
  FileText,
  Layers,
  MapPin,
  User,
  Package,
  DollarSign,
  Calendar,
  Info,
  Printer,
  FileCheck,
  AlertCircle,
  FolderOpen,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { profileService } from '../../services/profileService';
import { formatCurrency } from '../../utils/formatters';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

/* ─────────────────────────────────────────────
   پیکربندی وضعیت
   ───────────────────────────────────────────── */
const STATUS_MAP = {
  7:  { label: pageText.profile.orderDetailPage.statuses.s7,  color: 'amber' },
  8:  { label: pageText.profile.orderDetailPage.statuses.s8,  color: 'blue' },
  9:  { label: pageText.profile.orderDetailPage.statuses.s9,  color: 'red' },
  10: { label: pageText.profile.orderDetailPage.statuses.s10, color: 'blue' },
  11: { label: pageText.profile.orderDetailPage.statuses.s11, color: 'red' },
  12: { label: pageText.profile.orderDetailPage.statuses.s12, color: 'violet' },
  13: { label: pageText.profile.orderDetailPage.statuses.s13, color: 'emerald' },
  14: { label: pageText.profile.orderDetailPage.statuses.s14, color: 'red' },
  15: { label: pageText.profile.orderDetailPage.statuses.s15, color: 'emerald' },
  16: { label: pageText.profile.orderDetailPage.statuses.s16, color: 'slate' },
};

const getColor = (c) => ({
  bg: `bg-${c}-50`,
  text: `text-${c}-700`,
  dot: `bg-${c}-500`,
  ring: `ring-${c}-200/60`,
  border: `border-${c}-200`,
});

const SPEC_LABELS = {
  size: pageText.profile.orderDetailPage.specLabels.size,
  paper: pageText.profile.orderDetailPage.specLabels.paper,
  coating: pageText.profile.orderDetailPage.specLabels.coating,
  cutting: pageText.profile.orderDetailPage.specLabels.cutting,
  quantity: pageText.profile.orderDetailPage.specLabels.quantity,
  color_mode: pageText.profile.orderDetailPage.specLabels.color_mode,
  print_side: pageText.profile.orderDetailPage.specLabels.print_side,
  category: pageText.profile.orderDetailPage.specLabels.category,
  quantity_label: "تعداد کل",
  has_design: "دارای طراحی اختصاصی",
};

/* ─────────────────────────────────────────────
   انیمیشن‌ها
   ───────────────────────────────────────────── */
const stagger = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06, delayChildren: 0.08 } },
};
const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 260, damping: 24 } },
};

/* ═════════════════════════════════════════════
   OrderDetailPage
   ═════════════════════════════════════════════ */
const OrderDetailPage = () => {
  const { id } = useParams();

  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['order-detail', id],
    queryFn: () => profileService.getOrderDetails(id),
  });

  if (isLoading) return <DetailSkeleton />;

  if (isError || !order) {
    return (
      <div className="
        max-w-2xl mx-auto mt-10
        flex items-center gap-3
        bg-red-50 text-red-700
        p-5 rounded-2xl
        ring-1 ring-red-200/50
      ">
        <AlertCircle size={20} />
        <span className="text-sm font-bold">
          {pageText.profile.orderDetailPage.errorGettingOrder}
        </span>
      </div>
    );
  }

  const statusRaw = STATUS_MAP[order.current_status] || { label: pageText.profile.orderDetailPage.unknown, color: 'slate' };
  const sc = getColor(statusRaw.color);

  return (
    <motion.div
      variants={stagger}
      initial="hidden"
      animate="show"
      className="max-w-5xl mx-auto space-y-6"
    >
      {/* ════════════════ هدر ════════════════ */}
      <motion.header
        variants={fadeUp}
        className="
          flex flex-col md:flex-row md:items-center
          justify-between gap-4
          bg-white rounded-2xl
          ring-1 ring-black/[0.05]
          p-5 md:p-6
        "
      >
        <div className="flex items-center gap-4">
          <Link
            to="/profile/orders"
            className="
              w-10 h-10 flex items-center justify-center
              rounded-xl ring-1 ring-black/[0.06]
              text-slate-500 hover:text-primary
              hover:ring-primary/30 hover:bg-primary/5
              transition-all duration-200
            "
          >
            <ArrowRight size={20} />
          </Link>
          <div>
            <h1 className="text-lg md:text-xl font-extrabold text-slate-800 tracking-tight">
              {pageText.profile.orderDetailPage.orderDetail}{' '}
              <span className="text-primary">#{order.order_code}</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mt-1">
              <Calendar size={12} />
              {pageText.profile.orderDetailPage.registeredAt}{' '}
              {new Date(order.created_at).toLocaleDateString('EN')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto flex-wrap">
          {/* بج وضعیت */}
          <div className={`
            inline-flex items-center gap-2
            px-3.5 py-2 rounded-xl
            text-xs font-bold
            ring-1
            ${sc.bg} ${sc.text} ${sc.ring}
          `}>
            <div className={`w-2 h-2 rounded-full animate-pulse ${sc.dot}`} />
            {statusRaw.label}
          </div>

          {/* دکمه‌های فاکتور */}
          <Link
            to={`/profile/orders/${id}/quotation`}
            className="
              flex items-center gap-1.5
              px-3 py-2 rounded-xl
              text-xs font-bold text-slate-500
              ring-1 ring-black/[0.06]
              hover:text-primary hover:ring-primary/30 hover:bg-primary/5
              transition-all duration-200
            "
          >
            <Printer size={14} />
            {pageText.profile.orderDetailPage.quotation}
          </Link>
          <Link
            to={`/profile/orders/${id}/invoice`}
            className="
              hidden sm:flex items-center gap-1.5
              px-3 py-2 rounded-xl
              text-xs font-bold text-slate-500
              ring-1 ring-black/[0.06]
              hover:text-emerald-600 hover:ring-emerald-300 hover:bg-emerald-50
              transition-all duration-200
            "
          >
            <FileCheck size={14} />
            {pageText.profile.orderDetailPage.invoice}
          </Link>
        </div>
      </motion.header>

      {/* ════════════════ کارت‌های خلاصه ════════════════ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* قیمت کل */}
        <motion.div
          variants={fadeUp}
          className="
            bg-white rounded-2xl ring-1 ring-black/[0.05]
            p-6 flex flex-col items-center justify-center text-center
            space-y-2.5
          "
        >
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
            <span className='text-primary font-extralight text-lg pt-1' >IQD</span>
          </div>
          <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase">
            {pageText.profile.orderDetailPage.totalPrice}
          </span>
          <div className="text-2xl font-extrabold text-slate-800 tabular-nums">
            {formatCurrency(order.total_price)}
            <span className="text-xs font-bold text-slate-400 mx-1">{globalText.currency}</span>
          </div>
        </motion.div>

        {/* اطلاعات گیرنده */}
        <motion.div
          variants={fadeUp}
          className="
            bg-white rounded-2xl ring-1 ring-black/[0.05]
            p-6 lg:col-span-2 space-y-4
          "
        >
          <div className="flex items-center gap-2 text-sm font-bold text-slate-700 pb-3 border-b border-slate-100">
            <MapPin size={16} className="text-primary" />
            {pageText.profile.orderDetailPage.receiverInfo}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-slate-400 font-bold">
                {pageText.profile.orderDetailPage.receiver}
              </span>
              <span className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <User size={14} className="text-slate-300" />
                {pageText.profile.orderDetailPage.userCountOf} {order.user}
              </span>
            </div>
            <div className="flex flex-col gap-1.5 md:col-span-2 bg-slate-50/80 p-4 rounded-xl ring-1 ring-black/[0.03]">
              <span className="text-[10px] text-slate-400 font-bold">
                {pageText.profile.orderDetailPage.fullAddress}
              </span>
              <p className="text-sm text-slate-600 leading-relaxed">{order.full_address}</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ════════════════ آیتم‌های سفارش ════════════════ */}
      <motion.section variants={fadeUp} className="space-y-4">
        <h2 className="text-sm font-bold text-slate-700 flex items-center gap-2 px-1">
          <Layers size={17} className="text-primary" />
          {pageText.profile.orderDetailPage.orderItemList} ({order.order_item?.length})
        </h2>

        {order.order_item?.map((item) => (
          <OrderItemCard key={item.id} item={item} />
        ))}
      </motion.section>
    </motion.div>
  );
};

/* ═════════════════════════════════════════════
   کارت آیتم سفارش
   ═════════════════════════════════════════════ */
/* ═════════════════════════════════════════════
   کارت آیتم سفارش (اصلاح شده)
   ═════════════════════════════════════════════ */
   const getSpecLabel = (key) => {
    const labels = {
      quantity_label: "تیراژ/تعداد",
      has_design: "نیاز به طراحی اختصاصی",
    };
    return labels[key] || key;
  };
  
  const OrderItemCard = ({ item }) => {
    return (
      <div className="bg-white rounded-2xl ring-1 ring-black/[0.05] overflow-hidden hover:shadow-lg transition-all duration-300 mb-4">
        
        {/* هدر کارت: نام محصول و قیمت کل */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 bg-slate-50/50 border-b border-slate-100">
          <div className="flex items-center gap-3">
            {item.product?.image ? (
              <img 
                src={item.product.image} 
                alt={item.product?.name} 
                className="w-12 h-12 rounded-xl object-cover ring-1 ring-black/[0.05]"
              />
            ) : (
              <div className="w-12 h-12 rounded-xl bg-white ring-1 ring-black/[0.05] flex items-center justify-center text-blue-600">
                <Package size={22} />
              </div>
            )}
            <div>
              <h3 className="text-sm font-bold text-slate-800">
                {item.product?.name || item.name}
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5 font-medium">
                کد محصول: {item.product?.code || '---'}
              </p>
            </div>
          </div>
  
          <div className="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-extrabold tabular-nums shadow-sm " dir='ltr'>
            {Number(item.price).toLocaleString()} IQD
          </div> 
        </div>
  
{/* محتوای اصلی: انتخاب‌های کاربر */}
<div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* بخش اول: مشخصات و آپشن‌های انتخابی محصول */}
          <div>

            
            <div className="flex flex-wrap gap-2">
              {item.specs?.options_detail && item.specs.options_detail.length > 0 ? (
                item.specs.options_detail.map((opt, idx) => (
                  <div 
                    key={idx} 
                    className="flex items-center gap-2 bg-slate-50/80 ring-1 ring-black/[0.04] px-3 py-1.5 rounded-lg"
                  >
                    <span className="text-[10px] text-slate-400 font-bold">
                      {opt.option_group}:
                    </span>
                    <span className="text-xs text-slate-700 font-semibold">
                      {opt.selections?.[0]?.label || '---'}
                    </span>
                  </div>
                ))
              ) : (
                <div className="w-full flex items-center gap-2 bg-slate-50/50 border border-dashed border-slate-200 p-3 rounded-xl">
                </div>
              )}
            </div>
          </div>
  
          {/* بخش دوم: فایل‌های طراحی آپلود شده توسط کاربر */}
          <div>

  
            <div className="space-y-2">
              {item.design_files && item.design_files.length > 0 ? (
                item.design_files.map((file, index) => (
                  <a
                    key={file.id}
                    href={file.file_url}
                    target="_blank"
                    rel="noreferrer"
                    className="group flex items-center justify-between p-3 rounded-xl bg-slate-50 ring-1 ring-black/[0.02] hover:ring-indigo-200 hover:bg-indigo-50/30 transition-all duration-200"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-9 h-9 rounded-lg bg-white ring-1 ring-black/[0.04] flex items-center justify-center text-slate-400 group-hover:text-indigo-600 transition-colors">
                        <FileText size={18} />
                      </div>
                      <span className="text-xs font-bold text-slate-700 truncate dir-ltr text-right">
                       {index + 1}
                      </span>
                    </div>
                    <Download size={16} className="text-slate-400 group-hover:text-indigo-600 transition-colors" />
                  </a>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-6 rounded-xl bg-slate-50/50 border border-dashed border-slate-200">
                  <p className="text-xs text-slate-400 font-medium">هیچ فایلێک بۆ ئەم داواکارییە تۆمار نەکراوە</p>
                </div>
              )}
            </div>
          </div>
  
        </div>
      </div>
    );
  };

/* ─────────────────────────────────────────────
   کامپوننت‌های کمکی
   ───────────────────────────────────────────── */
const SectionLabel = ({ children, color = 'primary' }) => (
  <h4 className="
    text-[10px] font-extrabold text-slate-400
    uppercase tracking-[0.15em]
    flex items-center gap-2
  ">
    <div className={`w-1 h-3.5 rounded-full bg-${color}-500`} />
    {children}
  </h4>
);

const SpecBadge = ({ label, value }) => (
  <div className="
    flex items-center gap-2
    bg-slate-50/80 ring-1 ring-black/[0.04]
    px-3 py-1.5 rounded-lg
  ">
    <span className="text-[10px] text-slate-400 font-bold">
      {SPEC_LABELS[label] || label}:
    </span>
    <span className="text-xs text-slate-700 font-semibold">{value}</span>
  </div>
);

/* ═════════════════════════════════════════════
   اسکلتون
   ═════════════════════════════════════════════ */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent';

const DetailSkeleton = () => (
  <div className="max-w-5xl mx-auto space-y-6">
    {/* هدر */}
    <div className="bg-white rounded-2xl ring-1 ring-black/[0.04] p-6 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-xl bg-slate-100 ${shimmer}`} />
      <div className="space-y-2 flex-1">
        <div className={`h-6 w-48 bg-slate-100 rounded-lg ${shimmer}`} />
        <div className={`h-3 w-28 bg-slate-50 rounded ${shimmer}`} />
      </div>
      <div className={`h-9 w-24 bg-slate-100 rounded-xl ${shimmer}`} />
    </div>
    {/* کارت‌ها */}
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className={`h-36 bg-white rounded-2xl ring-1 ring-black/[0.04] ${shimmer}`} />
      <div className={`h-36 bg-white rounded-2xl ring-1 ring-black/[0.04] lg:col-span-2 ${shimmer}`} />
    </div>
    {/* آیتم‌ها */}
    {[1, 2].map((i) => (
      <div key={i} className="bg-white rounded-2xl ring-1 ring-black/[0.04] overflow-hidden">
        <div className={`h-16 bg-slate-50 border-b border-slate-100 ${shimmer}`} />
        <div className="p-5 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className={`h-4 w-32 bg-slate-100 rounded ${shimmer}`} />
            <div className="flex flex-wrap gap-2">
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className={`h-7 w-24 bg-slate-50 rounded-lg ${shimmer}`} />
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <div className={`h-4 w-28 bg-slate-100 rounded ${shimmer}`} />
            <div className={`h-14 bg-slate-50 rounded-xl ${shimmer}`} />
          </div>
        </div>
      </div>
    ))}
  </div>
);

export default OrderDetailPage;