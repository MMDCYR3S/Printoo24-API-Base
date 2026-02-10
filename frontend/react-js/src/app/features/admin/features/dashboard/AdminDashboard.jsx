// const DashboardPage = () => {
//   return (
//     <div className="space-y-6">
//       <h1 className="text-3xl font-bold text-gray-800">داشبورد مدیریت</h1>
      
//       <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//         {/* کارت‌های آماری نمونه */}
//         <div className="stat bg-base-100 shadow rounded-box">
//           <div className="stat-title">فروش کل</div>
//           <div className="stat-value text-primary">25.6M</div>
//           <div className="stat-desc">21% بیشتر از ماه قبل</div>
//         </div>
        
//         <div className="stat bg-base-100 shadow rounded-box">
//           <div className="stat-title">کاربران جدید</div>
//           <div className="stat-value text-secondary">4,200</div>
//           <div className="stat-desc">↗︎ 400 (22%)</div>
//         </div>

//         <div className="stat bg-base-100 shadow rounded-box">
//           <div className="stat-title">سفارشات باز</div>
//           <div className="stat-value">1,200</div>
//           <div className="stat-desc">↘︎ 90 (14%)</div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default DashboardPage;




import React from 'react';
import { 
  TrendingUp, TrendingDown, Users, ShoppingCart, 
  Box, DollarSign, RefreshCw, Layers, Activity, Calendar
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, 
  BarChart, Bar, Cell, PieChart, Pie 
} from 'recharts';
import clsx from 'clsx';
import { useDashboardStats } from '../../hooks/useDashboardStats';

// --- Helper Functions ---
const formatPrice = (value) => new Intl.NumberFormat('fa-IQ').format(value);
const formatNumber = (value) => new Intl.NumberFormat('fa-IR').format(value);

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
      {trend === 'down' && <span className="text-rose-500 bg-rose-50 px-2 py-1 rounded-lg flex items-center gap-1"><TrendingDown size={14}/> {trendValue}%</span>}
      {trend === 'neutral' && <span className="text-slate-500 bg-slate-50 px-2 py-1 rounded-lg flex items-center gap-1"><Activity size={14}/> {trendValue}</span>}
      <span className="text-slate-400">{trendLabel}</span>
    </div>

    {subValue && <div className="mt-3 text-xs text-slate-400 border-t border-slate-50 pt-3">{subValue}</div>}
  </div>
);

// 2. نمودار فروش (Financial Chart)
const FinancialChart = ({ data }) => {
  if (!data || data.length === 0) return <div className="h-64 flex items-center justify-center text-slate-300">داده‌ای برای نمایش وجود ندارد</div>;

  return (
    <div className="h-[300px] w-full dir-ltr">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#164A41" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#164A41" stopOpacity={0}/>
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
            itemStyle={{ color: '#164A41', fontWeight: 'bold', fontSize: '14px' }}
            formatter={(value) => [`${new Intl.NumberFormat('en-US').format(value)} IQD`, 'فروش']}
          />
          <Area 
            type="monotone" 
            dataKey="amount" 
            stroke="#164A41" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorRevenue)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// 3. نمودار توزیع سفارشات (Status Chart)
const OrderStatusChart = ({ data }) => {
  // تبدیل دیتا به فرمت Recharts
  const chartData = data?.map(d => ({
    name: d.status,
    value: d.count,
    color: d.status === 'Completed' ? '#10b981' : 
           d.status === 'Pending' ? '#f59e0b' : 
           d.status === 'Processing' ? '#3b82f6' : '#ef4444'
  })) || [];

  return (
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
      {/* متن وسط دونات */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-black text-slate-800">{chartData.reduce((acc, curr) => acc + curr.value, 0)}</span>
          <span className="text-[10px] text-slate-400 font-bold">کل سفارشات</span>
      </div>
    </div>
  );
};


// --- Main Page Component ---
const AdminDashboard = () => {
  const { orders, products, financial, users, isLoading, isError, refetchAll } = useDashboardStats();

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
    <div className="p-6 md:p-8 max-w-[1920px] mx-auto space-y-8 pb-32 animate-fade-in-up">
      
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
                <Calendar size={14}/> {new Date().toLocaleDateString('fa-IR', { weekday: 'long', day: 'numeric', month: 'long' })}
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
             subValue={`میانگین هر سفارش: ${formatPrice(financial?.summary?.average_order_value || 0)} IQD`}
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

      {/* --- Row 2: Charts & Details --- */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Left: Financial Chart (2/3 width) */}
          <div className="xl:col-span-2 bg-white p-6 md:p-8 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40">
              <div className="flex justify-between items-center mb-8">
                  <div>
                      <h3 className="font-bold text-xl text-slate-800">نمودار فروش ۳۰ روز گذشته</h3>
                      <p className="text-xs text-slate-400 mt-1">روند درآمدزایی فروشگاه</p>
                  </div>
                  <div className="flex gap-2">
                      <span className="badge badge-lg bg-emerald-50 text-emerald-700 border-0 font-bold px-4">
                          مجموع: {formatPrice(financial?.summary?.total_revenue || 0)} IQD
                      </span>
                  </div>
              </div>
              <FinancialChart data={financial?.chart_data} />
          </div>

          {/* Right: Order Status (1/3 width) */}
          <div className="bg-white p-6 md:p-8 rounded-[2rem] border border-slate-100 shadow-xl shadow-slate-200/40 flex flex-col">
              <h3 className="font-bold text-xl text-slate-800 mb-6">وضعیت سفارشات</h3>
              <div className="flex-1 flex flex-col justify-center">
                  <OrderStatusChart data={orders?.status_breakdown} />
                  
                  {/* Legend */}
                  <div className="mt-8 space-y-3">
                      {orders?.status_breakdown?.map((status, idx) => {
                          const colors = {
                             'Completed': 'bg-emerald-500',
                             'Pending': 'bg-amber-500',
                             'Processing': 'bg-blue-500',
                             'Canceled': 'bg-red-500'
                          };
                          const labels = {
                             'Completed': 'تکمیل شده',
                             'Pending': 'در انتظار',
                             'Processing': 'در حال پردازش',
                             'Canceled': 'لغو شده'
                          };
                          return (
                              <div key={idx} className="flex justify-between items-center text-sm">
                                  <div className="flex items-center gap-2">
                                      <span className={`w-2 h-2 rounded-full ${colors[status.status] || 'bg-slate-400'}`}></span>
                                      <span className="text-slate-600 font-medium">{labels[status.status] || status.status}</span>
                                  </div>
                                  <span className="font-bold text-slate-800">{status.count}</span>
                              </div>
                          )
                      })}
                  </div>
              </div>
          </div>
      </div>

      {/* --- Row 3: Secondary Stats --- */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* User Roles Breakdown */}
          <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
               <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                   <Users size={18} className="text-primary"/> تفکیک کاربران
               </h4>
               <div className="space-y-4">
                   {users?.role_breakdown?.map((role, idx) => (
                       <div key={idx} className="flex items-center gap-4">
                           <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400 font-bold">
                               {role.count}
                           </div>
                           <div className="flex-1">
                               <div className="flex justify-between mb-1">
                                   <span className="text-sm font-bold text-slate-700">{role.role}</span>
                                   <span className="text-xs text-slate-400">{Math.round((role.count / users.summary.total_users) * 100)}%</span>
                               </div>
                               <progress className="progress progress-primary w-full" value={role.count} max={users.summary.total_users}></progress>
                           </div>
                       </div>
                   ))}
               </div>
          </div>

          {/* Product Config Stats */}
          <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
               <h4 className="font-bold text-slate-800 mb-4 flex items-center gap-2">
                   <Layers size={18} className="text-primary"/> پیکربندی محصولات
               </h4>
               <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-blue-50 rounded-2xl border border-blue-100">
                       <span className="text-blue-500 text-xs font-bold block mb-1">فروش تیراژی (پکی)</span>
                       <span className="text-2xl font-black text-blue-700">{products?.configuration_breakdown?.with_quantity || 0}</span>
                       <span className="text-[10px] text-blue-400 block mt-1">محصول</span>
                   </div>
                   <div className="p-4 bg-purple-50 rounded-2xl border border-purple-100">
                       <span className="text-purple-500 text-xs font-bold block mb-1">فروش تعدادی (آزاد)</span>
                       <span className="text-2xl font-black text-purple-700">{products?.configuration_breakdown?.without_quantity || 0}</span>
                       <span className="text-[10px] text-purple-400 block mt-1">محصول</span>
                   </div>
               </div>
               <div className="mt-4 p-4 bg-slate-50 rounded-2xl flex items-center justify-between text-sm text-slate-600">
                   <span>محصولات غیرفعال:</span>
                   <span className="font-bold text-error">{products?.status_breakdown?.inactive} مورد</span>
               </div>
          </div>

      </div>

    </div>
  );
};

export default AdminDashboard;