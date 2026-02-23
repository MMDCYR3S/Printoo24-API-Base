import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShoppingBag,
  CreditCard,
  ShieldCheck,
  AlertCircle,
  ArrowLeft,
  PackageOpen,
  Sparkles,
  Info,
  Receipt,
  Lock,
} from 'lucide-react';
import { cartService } from '../../services/cartService';
import CartItem from './components/CartItem';
import { toast } from 'react-hot-toast';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

/* ─────────────────────────────────────────────
   انیمیشن‌ها
   ───────────────────────────────────────────── */
const staggerList = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.05 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 260, damping: 24 },
  },
  exit: {
    opacity: 0,
    x: -30,
    transition: { duration: 0.2 },
  },
};

/* ═════════════════════════════════════════════
   CartPage
   ═════════════════════════════════════════════ */
const CartPage = () => {
  const [cartData, setCartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  const t = pageText.cart.cartPage;

  const fetchCart = useCallback(async () => {
    try {
      setLoading(true);
      const data = await cartService.getCartItems();
      setCartData(data);
    } catch (err) {
      console.error(err);
      toast.error(t.fetchCartError);
    } finally {
      setLoading(false);
    }
  }, [t.fetchCartError]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleDeleteItem = useCallback(
    async (itemId) => {
      if (!window.confirm(t.deleteConfirm)) return;
      setDeletingId(itemId);
      try {
        await cartService.deleteItem(itemId);
        toast.success(t.deleteSuccess);
        fetchCart();
      } catch (err) {
        toast.error(t.deleteError);
      } finally {
        setDeletingId(null);
      }
    },
    [t, fetchCart]
  );

  /* ── لودینگ ── */
  if (loading) return <CartSkeleton />;

  /* ── سبد خالی ── */
  if (!cartData?.items?.length) return <EmptyCart />;

  const itemsWithoutFiles = cartData.items.filter(
    (item) => !item.uploads || item.uploads.length === 0
  );
  const formattedTotal = cartData.total_price?.toLocaleString();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100/50 pb-28 lg:pb-8 pt-6 md:pt-8">
      <div className="container mx-auto px-4 max-w-7xl">

        {/* ── هدر ── */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-6 md:mb-8"
        >
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-primary/10 flex items-center justify-center">
              <ShoppingBag size={20} className="text-primary" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-extrabold text-slate-800">
                {t.pageTitle}
              </h1>
              <p className="text-xs text-slate-400 font-medium mt-0.5">
                {t.productUnit.replace('{{count}}', cartData.items.length)}
              </p>
            </div>
          </div>

          <Link
            to="/shop"
            className="
              hidden sm:flex items-center gap-1.5
              text-sm font-bold text-primary/70 hover:text-primary
              px-3 py-1.5 rounded-lg hover:bg-primary/5
              transition-all duration-200
            "
          >
            ادامه خرید
            <ArrowLeft size={14} />
          </Link>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">

          {/* ════════════════ لیست آیتم‌ها ════════════════ */}
          <div className="lg:col-span-8">
            <motion.div
              variants={staggerList}
              initial="hidden"
              animate="show"
              className="space-y-3 md:space-y-4"
            >
              <AnimatePresence mode="popLayout">
                {cartData.items.map((item) => (
                  <motion.div
                    key={item.id}
                    variants={fadeUp}
                    exit="exit"
                    layout
                  >
                    <CartItem
                      item={item}
                      onDelete={handleDeleteItem}
                      isDeleting={deletingId === item.id}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* ════════════════ خلاصه سفارش (دسکتاپ) ════════════════ */}
          <div className="lg:col-span-4 hidden lg:block">
            <div className="sticky top-24 space-y-4">
              <OrderSummary
                cartData={cartData}
                formattedTotal={formattedTotal}
                itemsWithoutFiles={itemsWithoutFiles}
                onCheckout={() => navigate('/checkout')}
                t={t}
              />
            </div>
          </div>
        </div>
      </div>

      {/* ════════════════ Bottom Bar موبایل ════════════════ */}
      <div className="
        fixed bottom-0 left-0 w-full z-40
        lg:hidden
        bg-white/90 backdrop-blur-xl
        border-t border-slate-200/60
        shadow-[0_-4px_20px_-4px_rgba(0,0,0,0.08)]
      ">
        <div className="container mx-auto px-4 py-3 flex items-center gap-4">
          <div className="flex-1 min-w-0">
            <p className="text-[10px] text-slate-400 font-medium">{t.totalPayableLabel}</p>
            <div className="flex items-baseline gap-1">
              <span className="text-lg font-extrabold text-slate-800">
                {formattedTotal}
              </span>
              <span className="text-[10px] font-bold text-slate-400">
                {t.currency}
              </span>
            </div>
          </div>
          <button
            onClick={() => navigate('/checkout')}
            className="
              flex items-center justify-center gap-2
              px-6 py-3 rounded-xl
              bg-primary text-white text-sm font-bold
              shadow-md shadow-primary/20
              hover:shadow-lg hover:shadow-primary/30
              active:scale-[0.97]
              transition-all duration-200
            "
          >
            {t.checkoutBtn}
            <ArrowLeft size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};

/* ═════════════════════════════════════════════
   خلاصه سفارش
   ═════════════════════════════════════════════ */
const OrderSummary = ({ cartData, formattedTotal, itemsWithoutFiles, onCheckout, t }) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.15 }}
    className="
      bg-white rounded-2xl overflow-hidden
      ring-1 ring-black/[0.04]
      shadow-sm
    "
  >
    {/* هدر */}
    <div className="px-6 py-4 border-b border-slate-100/80 flex items-center gap-2.5">
      <Receipt size={18} className="text-blue-500" />
      <h2 className="text-[15px] font-bold text-slate-800">{t.summaryTitle}</h2>
    </div>

    <div className="p-6 space-y-5">
      {/* ردیف‌ها */}
      <div className="space-y-3">
        <SummaryRow label={t.itemCountLabel} value={cartData.items.length} />
        <SummaryRow
          label={t.subtotalLabel}
          value={
            <span className="flex items-baseline gap-1">
              <span className="font-bold text-slate-700">{formattedTotal}</span>
              <span className="text-[10px] text-slate-400">{t.currency}</span>
            </span>
          }
        />
      </div>

      {/* جمع کل */}
      <div className="
        border-t border-dashed border-slate-200 pt-4
        flex items-center justify-between
      ">
        <span className="text-sm font-bold text-slate-600">{t.totalPayableLabel}</span>
        <div className="text-left">
          <span className="block text-2xl font-extrabold text-primary tracking-tight">
            {formattedTotal}
          </span>
          <span className="text-[10px] font-bold text-slate-400">{t.currency}</span>
        </div>
      </div>

      {/* هشدار فایل */}
      <AnimatePresence>
        {itemsWithoutFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="
              flex items-start gap-2.5
              bg-blue-50/80 text-blue-700
              text-xs leading-relaxed font-medium
              p-3.5 rounded-xl
              ring-1 ring-blue-100/60
            ">
              <Info size={15} className="shrink-0 mt-0.5 text-blue-500" />
              <p>{t.noFileWarning.replace('{{count}}', itemsWithoutFiles.length)}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* دکمه پرداخت */}
      <button
        onClick={onCheckout}
        className="
          w-full flex items-center justify-center gap-2
          py-3.5 rounded-xl
          bg-primary text-white
          text-[15px] font-bold
          shadow-lg shadow-primary/20
          hover:shadow-xl hover:shadow-primary/30
          hover:-translate-y-[1px]
          active:translate-y-0 active:shadow-md
          transition-all duration-200
        "
      >
        <Lock size={15} />
        {t.checkoutBtn}
      </button>

      {/* اعتماد */}

    </div>
  </motion.div>
);

const SummaryRow = ({ label, value }) => (
  <div className="flex items-center justify-between text-sm">
    <span className="text-slate-500">{label}</span>
    <span className="font-semibold text-slate-700">
      {typeof value === 'number' ? value : value}
    </span>
  </div>
);

/* ═════════════════════════════════════════════
   سبد خالی
   ═════════════════════════════════════════════ */
const EmptyCart = () => (
  <div className="min-h-[80vh] flex flex-col items-center justify-center p-4 bg-gradient-to-b from-slate-50 to-white">
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      className="flex flex-col items-center text-center"
    >
      <div className="
        w-24 h-24 rounded-3xl
        bg-gradient-to-br from-slate-100 to-slate-50
        ring-1 ring-black/[0.04]
        flex items-center justify-center mb-6
      ">
        <PackageOpen size={40} strokeWidth={1.2} className="text-slate-300" />
      </div>
      <h1 className="text-xl font-extrabold text-slate-700 mb-2">
        {pageText.cart.cartPage.emptyCartTitle}
      </h1>
      <p className="text-sm text-slate-400 font-medium mb-6 max-w-xs">
        هنوز محصولی به سبد خریدتون اضافه نکردید
      </p>
      <Link
        to="/shop"
        className="
          inline-flex items-center gap-2
          px-6 py-2.5 rounded-xl
          bg-primary text-white text-sm font-bold
          shadow-md shadow-primary/20
          hover:shadow-lg hover:shadow-primary/30
          hover:-translate-y-[1px]
          active:translate-y-0
          transition-all duration-200
        "
      >
        <Sparkles size={15} />
        {pageText.cart.cartPage.viewProducts}
      </Link>
    </motion.div>
  </div>
);

/* ═════════════════════════════════════════════
   اسکلتون
   ═════════════════════════════════════════════ */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent';

const CartSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100/50 pt-8">
    <div className="container mx-auto px-4 max-w-7xl">
      {/* هدر */}
      <div className="flex items-center gap-3 mb-8">
        <div className={`w-11 h-11 bg-slate-100 rounded-2xl ${shimmer}`} />
        <div className="space-y-2">
          <div className={`h-6 w-32 bg-slate-100 rounded-lg ${shimmer}`} />
          <div className={`h-3 w-20 bg-slate-50 rounded-lg ${shimmer}`} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* آیتم‌ها */}
        <div className="lg:col-span-8 space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-2xl ring-1 ring-black/[0.04] p-4 flex gap-4"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className={`w-24 h-24 rounded-xl bg-slate-100 shrink-0 ${shimmer}`} />
              <div className="flex-1 space-y-3">
                <div className={`h-4 w-3/4 bg-slate-100 rounded-lg ${shimmer}`} />
                <div className={`h-3 w-1/2 bg-slate-50 rounded-lg ${shimmer}`} />
                <div className={`h-5 w-28 bg-slate-100 rounded-lg ${shimmer}`} />
              </div>
            </div>
          ))}
        </div>

        {/* خلاصه */}
        <div className="lg:col-span-4 hidden lg:block">
          <div className="bg-white rounded-2xl ring-1 ring-black/[0.04] p-6 space-y-4">
            <div className={`h-5 w-28 bg-slate-100 rounded-lg ${shimmer}`} />
            <div className="space-y-3">
              <div className="flex justify-between">
                <div className={`h-4 w-20 bg-slate-50 rounded ${shimmer}`} />
                <div className={`h-4 w-8 bg-slate-50 rounded ${shimmer}`} />
              </div>
              <div className="flex justify-between">
                <div className={`h-4 w-24 bg-slate-50 rounded ${shimmer}`} />
                <div className={`h-4 w-20 bg-slate-50 rounded ${shimmer}`} />
              </div>
            </div>
            <div className={`h-12 w-full bg-slate-100 rounded-xl ${shimmer}`} />
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default CartPage;