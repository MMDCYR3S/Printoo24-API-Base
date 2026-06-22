import React from 'react';
import { 
  TrendingUp, TrendingDown, Users, ShoppingCart, 
  Box, DollarSign, RefreshCw, Layers, Activity, Calendar,
  Wallet, ArrowDownCircle, BarChart2, CreditCard
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  BarChart, Bar, Cell, PieChart, Pie 
} from 'recharts';
import clsx from 'clsx';
import { useDashboardStats } from '../../hooks/useDashboardStats';

// --- Helper Functions ---
const formatPrice = (value) => new Intl.NumberFormat('fa-IQ').format(value);
const formatNumber = (value) => new Intl.NumberFormat('EN').format(value);

// --- Sub-Components ---

// 1. کارت آمار اصلی (Stat Card)
const StatCard = ({ title, value, subValue, icon: Icon, colorClass, trend, trendValue, trendLabel }) => (
  <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition-all duration-300 relative overflow-hidden group">
    <div className={`absolute top-0 right-0 w-24 h-24 rounded-bl-full opacity-10 transition-transform group-hover:scale-110 ${colorClass}`}></div>
    
    <div className="flex justify-between items-start relative z-10">
      <div>
        <p className="text-slate-500 text-sm font-bold mb-1">{title}</p>
        <h3 className="text-3xl font-black text-slate-800 dir-ltr text-right font-mono tracking-tight">
          {value}
        </h3>
      </div>
      <div className={`p-3 rounded-2xl ${colorClass} bg-opacity-20 text-opacity-100`}>
        <Icon size={24} className="opacity-80"/>
      </div>
    </div>

    <div className="mt-4 flex items-center gap-2 text-xs font-medium relative z-10">
      {trend === 'up' && <span className="text-emerald-500 bg-emerald-50 px-2 py-1 rounded-lg flex items-center gap-1"><TrendingUp size={14}/> {trendValue}%</span>}
      {trend === 'down' && <span className="text-rose-500 bg-rose-50 px-2 py-1 rounded-lg flex items-center gap-1"><TrendingDown size={14}/> {Math.abs(trendValue)}%</span>}
      {trend === 'neutral' && <span className="text-slate-500 bg-slate-50 px-2 py-1 rounded-lg flex items-center gap-1"><Activity size={14}/> {trendValue}</span>}
      <span className="text-slate-400">{trendLabel}</span>
    </div>

    {subValue && <div className="mt-3 text-xs text-slate-400 border-t border-slate-50 pt-3">{subValue}</div>}
  </div>
);

// 2. کارت سود/هزینه ساده
const MiniStatCard = ({ title, value, icon: Icon, colorClass, bgClass, unit }) => (
  <div className={`p-5 rounded-2xl border ${bgClass} flex items-center gap-4`}>
    <div className={`p-3 rounded-xl ${colorClass} bg-opacity-20`}>
      <Icon size={20} className="opacity-80"/>
    </div>
    <div>
      <p className="text-xs font-bold text-slate-500 mb-0.5">{title}</p>
      <p className="text-xl font-black text-slate-800 font-mono">{value} <span className="text-xs font-medium text-slate-400">{unit}</span></p>
    </div>
  </div>
);

// 3. نمودار فروش (Financial Chart)
const FinancialChart = ({ data }) => {
  if (!data || data.length === 0) return (
    <div className="h-64 flex items-center justify-center text-slate-300">داده‌ای برای نمایش وجود ندارد</div>
  );

  return (
    <div className="h-[300px] w-full dir-ltr">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#164A41" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#164A41" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorPaid" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.15}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9"/>
          <XAxis 
            dataKey="date" 
            axisLine={false} 
            tickLine={false} 
            tick={{fill: '#94a3b8', fontSize: 10}} 
            dy={10}
          />
          <YAxis 
            axisLine={false} 
            tickLine={false} 
            tick={{fill: '#94a3b8', fontSize: 10}}
            tickFormatter={(value) => `${value / 1000}k`} 
          />
          <RechartsTooltip 
            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            labelStyle={{ color: '#64748b', fontSize: '12px', marginBottom: '4px' }}
            itemStyle={{ fontWeight: 'bold', fontSize: '13px' }}
            formatter={(value, name) => [
              `${new Intl.NumberFormat('en-US').format(value)} IQD`,
              name === 'amount' ? 'فاکتور' : 'پرداخت شده'
            ]}
          />
          <Area 
            type="monotone" 
            dataKey="amount" 
            stroke="#164A41" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorRevenue)" 
          />
          <Area 
            type="monotone" 
            dataKey="paid" 
            stroke="#10b981" 
            strokeWidth={2}
            strokeDasharray="4 4"
            fillOpacity={1} 
            fill="url(#colorPaid)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// 4. نمودار دونات سفارشات
const PIE_COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'];

const OrderStatusChart = ({ data }) => {
  const chartData = (data || []).map((d, i) => ({
    name: d.status,
    value: d.count,
    color: PIE_COLORS[i % PIE_COLORS.length]
  }));

  const total = chartData.reduce((acc, curr) => acc + curr.value, 0);

  return (
    <div>
      <div className="h-[200px] w-full relative flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <RechartsTooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-black text-slate-800">{total}</span>
          <span className="text-[10px] text-slate-400 font-bold">کل سفارشات</span>
        </div>
      </div>

      {/* Legend - داینامیک از API */}
      <div className="mt-6 space-y-2.5">
        {chartData.map((item, idx) => (
          <div key={idx} className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }}></span>
              <span className="text-slate-600 font-medium text-xs">{item.name}</span>
            </div>
            <span className="font-bold text-slate-800">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- Main Page Component ---
const AdminDashboard = () => {
  const { orders, products, financial, users, expenses, profit, isLoading, isError, refetchAll } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-slate-50">
        <span className="loading loading-spinner loading-lg text-primary"></span>
        <p className="text-slate-400 animate-pulse font-medium">در حال دریافت و تحلیل داده‌های داشبورد...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-10 flex flex-col items-center justify-center h-[50vh] text-center">
        <div className="bg-red-50 p-4 rounded-full text-red-500 mb-4"><Activity size={32}/></div>
        <h3 className="font-bold text-lg text-slate-800">خطا در دریافت اطلاعات</h3>
        <p className="text-slate-500 mb-6 text-sm">ارتباط با سرور برقرار نشد.</p>
        <button onClick={refetchAll} className="btn btn-primary btn-sm gap-2">
          <RefreshCw size={16}/> تلاش مجدد
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto space-y-8 pb-32 animate-fade-in-up overflow-hidden">

      {/* --- Header --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-800 flex items-center gap-3">
            <span className="w-3 h-8 rounded-full bg-primary block shadow-lg shadow-primary/30"></span>
            داشبورد مدیریتی
          </h1>
          <p className="text-slate-500 mt-2 text-sm font-medium">
            آخرین وضعیت فروشگاه و آمار لحظه‌ای سیستم
          </p>
        </div>
        <div className="flex items-center gap-3 bg-white p-1.5 rounded-2xl border border-slate-100 shadow-sm">
          <span className="text-xs font-bold text-slate-400 px-3 flex items-center gap-2">
            <Calendar size={14}/> {new Date().toLocaleDateString('EN', { weekday: 'long', day: 'numeric', month: 'long' })}
          </span>
          <button onClick={refetchAll} className="btn btn-circle btn-ghost btn-sm text-primary hover:bg-primary/10 tooltip tooltip-left" data-tip="بروزرسانی">
            <RefreshCw size={18}/>
          </button>
        </div>
      </div>

      {/* --- Row 1: KPI Cards --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

        {/* 1. Revenue */}
        <StatCard 
          title="درآمد کل (ماه جاری)" 
          value={formatPrice(financial?.summary?.revenue_this_month || 0)}
          subValue={`میانگین هر فاکتور: ${formatPrice(financial?.summary?.average_invoice_value || 0)} IQD`}
          icon={DollarSign}
          colorClass="bg-emerald-500 text-emerald-600"
          trend={financial?.summary?.revenue_growth >= 0 ? 'up' : 'down'}
          trendValue={Math.abs(financial?.summary?.revenue_growth)}
          trendLabel="نسبت به ماه قبل"
        />

        {/* 2. Orders */}
        <StatCard 
          title="سفارشات جدید" 
          value={formatNumber(orders?.summary?.added_this_month || 0)}
          subValue={`${orders?.summary?.pending_approval_count} سفارش منتظر تایید اولیه`}
          icon={ShoppingCart}
          colorClass="bg-blue-500 text-blue-600"
          trend={orders?.summary?.growth_percentage >= 0 ? 'up' : 'down'}
          trendValue={Math.abs(orders?.summary?.growth_percentage)}
          trendLabel="رشد سفارشات"
        />

        {/* 3. Users */}
        <StatCard 
          title="کاربران جدید" 
          value={formatNumber(users?.summary?.new_this_month || 0)}
          subValue={`مجموع کل کاربران: ${formatNumber(users?.summary?.total_users)}`}
          icon={Users}
          colorClass="bg-purple-500 text-purple-600"
          trend={users?.summary?.growth_percentage >= 0 ? 'up' : 'down'}
          trendValue={Math.abs(users?.summary?.growth_percentage)}
          trendLabel="جذب کاربر"
        />

        {/* 4. Products */}
        <StatCard 
          title="محصولات" 
          value={formatNumber(products?.summary?.total_products || 0)}
          subValue={`${products?.status_breakdown?.active} محصول فعال در فروشگاه`}
          icon={Box}
          colorClass="bg-orange-500 text-orange-600"
          trend="neutral"
          trendValue={products?.summary?.added_this_month}
          trendLabel="محصول جدید این ماه"
        />
      </div>

      {/* --- Row 2: Financial Summary Cards --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">

        {/* پرداخت شده */}
        <MiniStatCard
          title="پرداخت شده"
          value={formatPrice(financial?.summary?.total_paid || 0)}
          icon={CreditCard}
          colorClass="bg-emerald-500 text-emerald-600"
          bgClass="bg-emerald-50 border-emerald-100"
          unit="IQD"
        />

        {/* مانده بدهکار */}
        <MiniStatCard
          title="مانده بدهکار (Outstanding)"
          value={formatPrice(financial?.summary?.outstanding || 0)}
          icon={Wallet}
          colorClass="bg-rose-500 text-rose-600"
          bgClass="bg-rose-50 border-rose-100"
          unit="IQD"
        />

        {/* هزینه‌های ماهانه */}
        <MiniStatCard
          title="هزینه‌های ماه جاری"
          value={formatPrice(expenses?.monthly_expenses || 0)}
          icon={ArrowDownCircle}
          colorClass="bg-amber-500 text-amber-600"
          bgClass="bg-amber-50 border-amber-100"
          unit="IQD"
        />

        {/* سود ماهانه */}
        <MiniStatCard
          title="سود ماه جاری"
          value={formatPrice(profit?.monthly_profit || 0)}
          icon={BarChart2}
          colorClass="bg-teal-500 text-teal-600"
          bgClass="bg-teal-50 border-teal-100"
          unit="IQD"
        />
      </div>

      {/* --- Row 3: Charts --- */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">

        {/* Left: Financial Chart (2/3 width) */}
        <div className="xl:col-span-2 bg-white p-6 md:p-8 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="font-bold text-xl text-slate-800">نمودار فروش و پرداخت‌ها</h3>
              <p className="text-xs text-slate-400 mt-1">خط نقطه‌چین = پرداخت شده</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="badge badge-lg bg-emerald-50 text-emerald-700 border-0 font-bold px-4">
                کل: {formatPrice(financial?.summary?.total_revenue || 0)} IQD
              </span>
              <span className="text-[10px] text-slate-400">
                سال جاری: {formatPrice(profit?.yearly_profit || 0)} IQD سود
              </span>
            </div>
          </div>
          <FinancialChart data={financial?.chart_data} />
        </div>

        {/* Right: Order Status (1/3 width) */}
        <div className="bg-white p-6 md:p-8 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 flex flex-col">
          <h3 className="font-bold text-xl text-slate-800 mb-2">وضعیت سفارشات</h3>
          <p className="text-xs text-slate-400 mb-4">مجموع: {orders?.summary?.total_orders} سفارش</p>
          <div className="flex-1 flex flex-col justify-center">
            <OrderStatusChart data={orders?.status_breakdown} />
          </div>
        </div>
      </div>

      {/* --- Row 4: Secondary Stats --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

        {/* User Roles Breakdown */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Users size={18} className="text-primary"/> تفکیک کاربران
          </h4>
          <div className="space-y-4">
            {users?.role_breakdown?.map((role, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-600 font-black text-sm">
                  {role.count}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-bold text-slate-700">{role.role || 'بدون نقش'}</span>
                    <span className="text-xs text-slate-400">
                      {Math.round((role.count / (users?.summary?.total_users || 1)) * 100)}%
                    </span>
                  </div>
                  <progress 
                    className="progress progress-primary w-full" 
                    value={role.count} 
                    max={users?.summary?.total_users || 1}
                  ></progress>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-slate-50 flex justify-between text-sm text-slate-500">
            <span>مشتریان: <strong className="text-slate-800">{users?.summary?.total_customers}</strong></span>
            <span>کارمندان: <strong className="text-slate-800">{users?.summary?.total_staff}</strong></span>
          </div>
        </div>

        {/* Product Config Stats */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Layers size={18} className="text-primary"/> پیکربندی محصولات
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 rounded-2xl border border-blue-100">
              <span className="text-blue-500 text-xs font-bold block mb-1">با تعداد (پکی)</span>
              <span className="text-2xl font-black text-blue-700">{products?.configuration_breakdown?.with_quantity || 0}</span>
              <span className="text-[10px] text-blue-400 block mt-1">محصول</span>
            </div>
            <div className="p-4 bg-purple-50 rounded-2xl border border-purple-100">
              <span className="text-purple-500 text-xs font-bold block mb-1">بدون تعداد (آزاد)</span>
              <span className="text-2xl font-black text-purple-700">{products?.configuration_breakdown?.without_quantity || 0}</span>
              <span className="text-[10px] text-purple-400 block mt-1">محصول</span>
            </div>
          </div>
          <div className="mt-4 p-4 bg-slate-50 rounded-2xl flex items-center justify-between text-sm text-slate-600">
            <span>محصولات غیرفعال:</span>
            <span className="font-bold text-error">{products?.status_breakdown?.inactive} مورد</span>
          </div>
          <div className="mt-2 p-4 bg-emerald-50 rounded-2xl flex items-center justify-between text-sm text-slate-600">
            <span>فعال:</span>
            <span className="font-bold text-emerald-600">{products?.status_breakdown?.active_percentage}%</span>
          </div>
        </div>

        {/* Profit & Expenses Summary */}
        <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
          <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart2 size={18} className="text-primary"/> خلاصه مالی
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-teal-50 rounded-xl border border-teal-100">
              <span className="text-xs font-bold text-teal-700">سود امروز</span>
              <span className="font-black text-teal-800 font-mono">{formatPrice(profit?.daily_profit || 0)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-teal-50 rounded-xl border border-teal-100">
              <span className="text-xs font-bold text-teal-700">سود ماه جاری</span>
              <span className="font-black text-teal-800 font-mono">{formatPrice(profit?.monthly_profit || 0)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-teal-50 rounded-xl border border-teal-100">
              <span className="text-xs font-bold text-teal-700">سود سالانه</span>
              <span className="font-black text-teal-800 font-mono">{formatPrice(profit?.yearly_profit || 0)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-amber-50 rounded-xl border border-amber-100">
              <span className="text-xs font-bold text-amber-700">هزینه روزانه</span>
              <span className="font-black text-amber-800 font-mono">{formatPrice(expenses?.daily_expenses || 0)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-amber-50 rounded-xl border border-amber-100">
              <span className="text-xs font-bold text-amber-700">هزینه سالانه</span>
              <span className="font-black text-amber-800 font-mono">{formatPrice(expenses?.yearly_expenses || 0)}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default AdminDashboard;