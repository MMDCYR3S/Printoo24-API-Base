import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Plus, Pencil, Trash2, X, Check, Search,
  TrendingDown, Calendar, DollarSign, Activity,
  ChevronDown, AlertCircle, RefreshCw, Filter
} from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { expenseService } from '../../services/expenseService';

// ─── Helpers ────────────────────────────────────────────────────────────────
const formatAmount = (val) =>
  new Intl.NumberFormat('fa-IQ').format(Number(val) || 0);

const toGregorianMonthYear = (dateStr) => {
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
};

const monthLabel = (key) => {
  const [y, m] = key.split('-');
  const date = new Date(Number(y), Number(m) - 1, 1);
  return date.toLocaleDateString('fa-IR', { year: 'numeric', month: 'long' });
};

const CURRENT_MONTH = toGregorianMonthYear(new Date().toISOString());

// ─── Searchable Dropdown ─────────────────────────────────────────────────────
const OrderDropdown = ({ invoices, value, onChange }) => {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef(null);

  const selected = invoices?.find((i) => i.id === value);

  const filtered = useMemo(() => {
    if (!invoices) return [];
    const q = search.toLowerCase();
    return invoices.filter(
      (i) =>
        i.order_code.toLowerCase().includes(q) ||
        i.customer_name.toLowerCase().includes(q) ||
        i.product_names.toLowerCase().includes(q)
    );
  }, [invoices, search]);

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between gap-2 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-right hover:border-primary/40 focus:outline-none focus:border-primary transition-colors"
      >
        <ChevronDown size={15} className={`text-slate-400 transition-transform shrink-0 ${open ? 'rotate-180' : ''}`} />
        <span className={`truncate ${selected ? 'text-slate-700 font-medium' : 'text-slate-400'}`}>
          {selected ? `${selected.order_code} — ${selected.customer_name}` : 'سفارشی انتخاب نشده (اختیاری)'}
        </span>
      </button>

      {open && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden">
          {/* سرچ */}
          <div className="p-2 border-b border-slate-100">
            <div className="flex items-center gap-2 px-3 py-2 bg-slate-50 rounded-xl">
              <Search size={14} className="text-slate-400 shrink-0" />
              <input
                autoFocus
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="جستجو در سفارشات..."
                className="flex-1 bg-transparent text-sm outline-none text-slate-700 text-right placeholder:text-slate-400"
              />
            </div>
          </div>

          {/* گزینه خالی */}
          <div className="max-h-52 overflow-y-auto">
            <button
              type="button"
              onClick={() => { onChange(null); setOpen(false); setSearch(''); }}
              className="w-full text-right px-4 py-2.5 text-sm text-slate-400 hover:bg-slate-50 transition-colors"
            >
              بدون سفارش
            </button>
            {filtered.length === 0 ? (
              <p className="text-center text-xs text-slate-400 py-4">نتیجه‌ای یافت نشد</p>
            ) : (
              filtered.map((inv) => (
                <button
                  key={inv.id}
                  type="button"
                  onClick={() => { onChange(inv.id); setOpen(false); setSearch(''); }}
                  className={`w-full text-right px-4 py-2.5 text-sm hover:bg-slate-50 transition-colors ${value === inv.id ? 'bg-primary/5 text-primary font-bold' : 'text-slate-700'}`}
                >
                  <div className="font-medium">{inv.order_code}</div>
                  <div className="text-xs text-slate-400 mt-0.5">{inv.customer_name} — {inv.product_names}</div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Modal (Add / Edit) ──────────────────────────────────────────────────────
const ExpenseModal = ({ open, onClose, editData, invoices, onSubmit, isSubmitting }) => {
  const [form, setForm] = useState({ name: '', amount: '', order: null });

  useEffect(() => {
    if (editData) {
      setForm({ name: editData.name, amount: editData.amount, order: editData.order ?? null });
    } else {
      setForm({ name: '', amount: '', order: null });
    }
  }, [editData, open]);

  if (!open) return null;

  const handleSubmit = () => {
    if (!form.name.trim() || !form.amount) return;
    const payload = { name: form.name, amount: String(form.amount) };
    if (form.order) payload.order = form.order;
    onSubmit(payload);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative w-full max-w-md bg-white rounded-[2rem] shadow-2xl p-6 space-y-5 animate-fade-in-up">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-800">
            {editData ? 'ویرایش هزینه' : 'ثبت هزینه جدید'}
          </h2>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm text-slate-400">
            <X size={18} />
          </button>
        </div>

        {/* نام هزینه */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-500">نام هزینه *</label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="مثلاً: هزینه چاپ، حمل‌ونقل..."
            className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-right focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* مبلغ */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-500">مبلغ (IQD) *</label>
          <input
            type="number"
            value={form.amount}
            onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
            placeholder="0"
            className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-left dir-ltr focus:outline-none focus:border-primary transition-colors"
          />
        </div>

        {/* سفارش */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-500">سفارش مرتبط (اختیاری)</label>
          <OrderDropdown invoices={invoices} value={form.order} onChange={(v) => setForm((f) => ({ ...f, order: v }))} />
        </div>

        {/* دکمه‌ها */}
        <div className="flex gap-3 pt-2">
          <button onClick={onClose} className="flex-1 btn btn-ghost btn-sm rounded-xl border border-slate-200 text-slate-500">
            انصراف
          </button>
          <button
            onClick={handleSubmit}
            disabled={!form.name.trim() || !form.amount || isSubmitting}
            className="flex-1 btn btn-primary btn-sm rounded-xl gap-2 shadow-lg shadow-primary/20"
          >
            {isSubmitting ? <span className="loading loading-spinner loading-xs" /> : <Check size={16} />}
            {editData ? 'ذخیره تغییرات' : 'ثبت هزینه'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── Delete Confirm ──────────────────────────────────────────────────────────
const DeleteConfirm = ({ open, onClose, onConfirm, isLoading }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-[2rem] shadow-2xl p-6 max-w-sm w-full space-y-4 text-center">
        <div className="w-14 h-14 bg-red-50 rounded-full flex items-center justify-center mx-auto text-red-500">
          <AlertCircle size={28} />
        </div>
        <h3 className="font-black text-slate-800 text-lg">حذف هزینه؟</h3>
        <p className="text-sm text-slate-500">این عملیات قابل بازگشت نیست.</p>
        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 btn btn-ghost btn-sm rounded-xl border border-slate-200">انصراف</button>
          <button onClick={onConfirm} disabled={isLoading} className="flex-1 btn btn-error btn-sm rounded-xl text-white gap-2">
            {isLoading ? <span className="loading loading-spinner loading-xs" /> : <Trash2 size={14} />}
            حذف
          </button>
        </div>
      </div>
    </div>
  );
};

// ─── Stat Card ───────────────────────────────────────────────────────────────
const StatCard = ({ title, value, icon: Icon, colorClass, sub }) => (
  <div className="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden group hover:shadow-md transition-all duration-300">
    <div className={`absolute top-0 right-0 w-20 h-20 rounded-bl-full opacity-10 ${colorClass} transition-transform group-hover:scale-110`} />
    <div className="flex items-start justify-between relative z-10">
      <div>
        <p className="text-xs font-bold text-slate-500 mb-1">{title}</p>
        <p className="text-2xl font-black text-slate-800 dir-ltr text-right font-mono">{formatAmount(value)}</p>
        {sub && <p className="text-[10px] text-slate-400 mt-1">{sub}</p>}
      </div>
      <div className={`p-2.5 rounded-xl ${colorClass} bg-opacity-20`}>
        <Icon size={20} className="opacity-70" />
      </div>
    </div>
  </div>
);

// ─── Main Page ───────────────────────────────────────────────────────────────
const ExpensePage = () => {
  const qc = useQueryClient();

  // state
  const [modalOpen, setModalOpen] = useState(false);
  const [editData, setEditData] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [filterMonth, setFilterMonth] = useState(CURRENT_MONTH); // '' = همه
  const [searchQuery, setSearchQuery] = useState('');

  // queries
  const { data: expenses = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['expenses'],
    queryFn: expenseService.getAll,
  });

  const { data: stats } = useQuery({
    queryKey: ['expenseStats'],
    queryFn: expenseService.getStatistics,
  });

  const { data: invoices = [] } = useQuery({
    queryKey: ['unlockedInvoices'],
    queryFn: expenseService.getUnlockedInvoices,
  });

  // mutations
  const createMutation = useMutation({
    mutationFn: expenseService.create,
    onSuccess: () => { qc.invalidateQueries(['expenses', 'expenseStats']); setModalOpen(false); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => expenseService.patch(id, payload),
    onSuccess: () => { qc.invalidateQueries(['expenses', 'expenseStats']); setModalOpen(false); setEditData(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: expenseService.remove,
    onSuccess: () => { qc.invalidateQueries(['expenses', 'expenseStats']); setDeleteTarget(null); },
  });

  // ─── فیلتر و گروه‌بندی ─────────────────────────────────────────────────
  const allMonths = useMemo(() => {
    const set = new Set(expenses.map((e) => toGregorianMonthYear(e.created_at)));
    return Array.from(set).sort((a, b) => b.localeCompare(a));
  }, [expenses]);

  const filtered = useMemo(() => {
    return expenses.filter((e) => {
      const monthMatch = !filterMonth || toGregorianMonthYear(e.created_at) === filterMonth;
      const searchMatch =
        !searchQuery ||
        e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (e.order_code || '').toLowerCase().includes(searchQuery.toLowerCase());
      return monthMatch && searchMatch;
    });
  }, [expenses, filterMonth, searchQuery]);

  const grouped = useMemo(() => {
    const map = {};
    filtered.forEach((e) => {
      const key = toGregorianMonthYear(e.created_at);
      if (!map[key]) map[key] = [];
      map[key].push(e);
    });
    return Object.entries(map).sort(([a], [b]) => b.localeCompare(a));
  }, [filtered]);

  const handleSubmit = (payload) => {
    if (editData) {
      updateMutation.mutate({ id: editData.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  // ─── Render ────────────────────────────────────────────────────────────
  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto space-y-8 pb-32 animate-fade-in-up">

      {/* ─── Header ─── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="w-3 h-8 rounded-full bg-rose-500 block shadow-lg shadow-rose-400/40" />
            مدیریت هزینه‌ها
          </h1>
          <p className="text-slate-500 mt-2 text-sm font-medium">ثبت، ویرایش و پیگیری هزینه‌های عملیاتی</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => { qc.invalidateQueries(['expenses', 'expenseStats']); }} className="btn btn-circle btn-ghost btn-sm text-slate-400 hover:bg-slate-100 bg-white border border-slate-100 shadow-sm">
            <RefreshCw size={16} />
          </button>
          <button
            onClick={() => { setEditData(null); setModalOpen(true); }}
            className="btn btn-primary btn-sm rounded-2xl gap-2 shadow-lg shadow-primary/25 px-5"
          >
            <Plus size={17} /> ثبت هزینه جدید
          </button>
        </div>
      </div>

      {/* ─── Stat Cards ─── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="کل هزینه‌ها" value={stats?.total_expenses} icon={TrendingDown} colorClass="bg-rose-500 text-rose-600" />
        <StatCard title="هزینه امروز" value={stats?.daily_expenses} icon={Calendar} colorClass="bg-amber-500 text-amber-600" sub="روزانه" />
        <StatCard title="هزینه این ماه" value={stats?.monthly_expenses} icon={Filter} colorClass="bg-blue-500 text-blue-600" sub="ماهانه" />
        <StatCard title="سود این ماه" value={stats?.monthly_profit} icon={DollarSign} colorClass="bg-emerald-500 text-emerald-600" sub={`سود سالانه: ${formatAmount(stats?.yearly_profit)} IQD`} />
      </div>

      {/* ─── Filters ─── */}
      <div className="bg-white p-4 rounded-3xl border border-slate-100 shadow-sm flex flex-col sm:flex-row gap-3 items-center">
        {/* سرچ */}
        <div className="flex-1 flex items-center gap-2 px-4 py-2.5 bg-slate-50 border border-slate-100 rounded-2xl">
          <Search size={15} className="text-slate-400 shrink-0" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="جستجو در نام هزینه یا کد سفارش..."
            className="flex-1 bg-transparent text-sm outline-none text-slate-700 text-right placeholder:text-slate-400"
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} className="text-slate-400 hover:text-slate-600">
              <X size={14} />
            </button>
          )}
        </div>

        {/* فیلتر ماه */}
        <div className="flex gap-2 flex-wrap justify-end">
          <button
            onClick={() => setFilterMonth('')}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${!filterMonth ? 'bg-primary text-white shadow-md shadow-primary/25' : 'bg-slate-50 text-slate-500 hover:bg-slate-100 border border-slate-200'}`}
          >
            همه ماه‌ها
          </button>
          {allMonths.map((m) => (
            <button
              key={m}
              onClick={() => setFilterMonth(m)}
              className={`px-4 py-2 text-xs font-bold rounded-xl transition-all ${filterMonth === m ? 'bg-primary text-white shadow-md shadow-primary/25' : 'bg-slate-50 text-slate-500 hover:bg-slate-100 border border-slate-200'}`}
            >
              {monthLabel(m)}
            </button>
          ))}
        </div>
      </div>

      {/* ─── Content ─── */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center h-52 gap-4">
          <span className="loading loading-spinner loading-lg text-primary" />
          <p className="text-slate-400 text-sm font-medium animate-pulse">در حال بارگذاری هزینه‌ها...</p>
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center h-52 gap-4 text-center">
          <div className="bg-red-50 p-4 rounded-full text-red-400"><Activity size={28} /></div>
          <p className="text-slate-600 font-bold">خطا در دریافت اطلاعات</p>
          <button onClick={refetch} className="btn btn-primary btn-sm rounded-xl gap-2">
            <RefreshCw size={14} /> تلاش مجدد
          </button>
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-52 gap-3 text-center">
          <div className="bg-slate-50 p-5 rounded-full text-slate-300"><TrendingDown size={32} /></div>
          <p className="text-slate-500 font-bold">هزینه‌ای ثبت نشده</p>
          <p className="text-slate-400 text-sm">با دکمه «ثبت هزینه جدید» اولین مورد را اضافه کنید</p>
        </div>
      ) : (
        <div className="space-y-8">
          {grouped.map(([monthKey, items]) => {
            const monthTotal = items.reduce((acc, e) => acc + Number(e.amount), 0);
            return (
              <div key={monthKey} className="space-y-3">
                {/* Month Header */}
                <div className="flex items-center justify-between px-1">
                  <div className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-rose-400" />
                    <h3 className="font-black text-slate-700 text-sm">{monthLabel(monthKey)}</h3>
                    <span className="badge badge-sm bg-slate-100 text-slate-500 border-0">{items.length} مورد</span>
                  </div>
                  <span className="text-sm font-black text-rose-500 dir-ltr">{formatAmount(monthTotal)} IQD</span>
                </div>

                {/* Expense Rows */}
                <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden divide-y divide-slate-50">
                  {items.map((expense) => (
                    <div
                      key={expense.id}
                      className="flex items-center gap-4 px-5 py-4 hover:bg-slate-50/70 transition-colors group"
                    >
                      {/* آیکون */}
                      <div className="w-10 h-10 rounded-2xl bg-rose-50 text-rose-400 flex items-center justify-center shrink-0">
                        <TrendingDown size={18} />
                      </div>

                      {/* اطلاعات */}
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-slate-800 text-sm truncate">{expense.name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          {expense.order_code ? (
                            <span className="text-xs text-primary bg-primary/5 px-2 py-0.5 rounded-lg font-medium">
                              {expense.order_code}
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">بدون سفارش</span>
                          )}
                          <span className="text-xs text-slate-400">
                            {new Date(expense.created_at).toLocaleDateString('fa-IR')}
                          </span>
                        </div>
                      </div>

                      {/* مبلغ */}
                      <div className="text-left shrink-0">
                        <p className="font-black text-rose-500 dir-ltr text-sm">{formatAmount(expense.amount)}</p>
                        <p className="text-[10px] text-slate-400 text-left">IQD</p>
                      </div>

                      {/* اکشن‌ها */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <button
                          onClick={() => { setEditData(expense); setModalOpen(true); }}
                          className="btn btn-ghost btn-xs btn-circle text-slate-400 hover:text-primary hover:bg-primary/10"
                        >
                          <Pencil size={14} />
                        </button>
                        <button
                          onClick={() => setDeleteTarget(expense.id)}
                          className="btn btn-ghost btn-xs btn-circle text-slate-400 hover:text-red-500 hover:bg-red-50"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ─── Modals ─── */}
      <ExpenseModal
        open={modalOpen}
        onClose={() => { setModalOpen(false); setEditData(null); }}
        editData={editData}
        invoices={invoices}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

      <DeleteConfirm
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};

export default ExpensePage;