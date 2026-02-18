import React from "react";
import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "../api/dashboardService";
import { 
  Wallet, TrendingUp, TrendingDown, ShoppingBag, 
  Users, Briefcase, Activity, CalendarDays, BarChart4
} from "lucide-react";
import StatusDonutChart from "../components/StatusDonutChart";
import { Skeleton } from "@/components/ui/skeleton";

// توابع کمکی
const formatPrice = (price) => Number(price).toLocaleString();
const formatCompactNumber = (number) => {
    return Intl.NumberFormat('fa-IR', {
        notation: "compact",
        maximumFractionDigits: 1
    }).format(number);
};

const AdminDashboard = () => {
  // دریافت اطلاعات داشبورد
  const { data: dashboardData, isLoading, isError } = useQuery({
    queryKey: ["adminDashboard"],
    queryFn: dashboardService.getAdminDashboard,
    refetchInterval: 60000, // رفرش خودکار هر ۱ دقیقه (برای زنده بودن داشبورد)
  });

  if (isLoading) return <DashboardSkeleton />;
  if (isError) return <div className="p-10 text-center text-red-500 font-bold">خطا در دریافت اطلاعات داشبورد.</div>;

  const { entity_counts, status_distribution, financial_summary } = dashboardData;

  // محاسبه حاشیه سود (Profit Margin)
  const revenue = financial_summary.system_revenue;
  const profit = financial_summary.system_profit;
  const margin = revenue > 0 ? ((profit / revenue) * 100).toFixed(1) : 0;

  return (
    <div className="p-4 md:p-6 space-y-6 max-w-[1600px] mx-auto animate-in fade-in duration-500 pb-20">
      
      {/* 1. HERO SECTION (سربرگ خوش‌آمدگویی) */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 bg-slate-900 p-6 md:p-8 rounded-2xl shadow-xl text-white relative overflow-hidden">
        {/* افکت گرافیکی پس‌زمینه */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-gold-dark/20 rounded-full blur-3xl -mr-20 -mt-20"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-500/20 rounded-full blur-3xl -ml-10 -mb-10"></div>
        
        <div className="relative z-10">
            <h1 className="text-2xl md:text-3xl font-black text-white mb-2 tracking-tight">
                نمای کلی سیستم (مدیریت کل)
            </h1>
            <p className="text-slate-400 text-sm flex items-center gap-2">
                <CalendarDays className="h-4 w-4" />
                امروز: {new Date().toLocaleDateString('fa-IR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
        </div>
        
        <div className="relative z-10 bg-white/10 backdrop-blur-md px-4 py-2 rounded-lg border border-white/10 flex items-center gap-3">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-xs font-bold text-slate-200 tracking-wider">سیستم آنلاین و پایدار است</span>
        </div>
      </div>

      {/* 2. FINANCIAL KPI CARDS (کارت‌های مالی) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KpiCard 
            title="کل درآمد سیستم" 
            value={formatPrice(revenue)} 
            unit="تومان"
            subtitle="از ابتدا تا کنون"
            icon={<Wallet className="text-emerald-500" />}
            trend="up"
            colorClass="border-emerald-200 bg-emerald-50/30"
            valueColor="text-emerald-700"
        />
        <KpiCard 
            title="کل هزینه‌ها" 
            value={formatPrice(financial_summary.system_cost)} 
            unit="تومان"
            subtitle="مواد اولیه، چاپ و لجستیک"
            icon={<TrendingDown className="text-rose-500" />}
            trend="down"
            colorClass="border-rose-200 bg-rose-50/30"
            valueColor="text-rose-700"
        />
        <KpiCard 
            title="سود خالص" 
            value={formatPrice(profit)} 
            unit="تومان"
            subtitle={`حاشیه سود: ${margin}٪`}
            icon={<TrendingUp className="text-gold-dark" />}
            trend="up"
            colorClass="border-amber-200 bg-amber-50/30"
            valueColor="text-amber-700"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* 3. CHARTS SECTION (نمودار وضعیت‌ها - ستون راست) */}
        <div className="xl:col-span-8 space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h2 className="text-lg font-black text-slate-800 flex items-center gap-2">
                            <Activity className="h-5 w-5 text-blue-500" />
                            توزیع وضعیت سفارشات
                        </h2>
                        <p className="text-xs text-slate-500 mt-1">نمایش وضعیت فعلی تمام سفارشات در جریان</p>
                    </div>
                    <div className="bg-slate-100 px-3 py-1 rounded text-xs font-bold text-slate-600">
                        مجموع: {entity_counts.total_orders} سفارش
                    </div>
                </div>
                
                <div className="flex flex-col md:flex-row items-center justify-center gap-8">
                    {/* نمودار */}
                    <div className="w-full md:w-1/2">
                        <StatusDonutChart data={status_distribution} />
                    </div>
                    
                    {/* لیست درصدی وضعیت‌ها */}
                    <div className="w-full md:w-1/2 space-y-3">
                        {status_distribution.map((status, index) => {
                            const percentage = ((status.count / entity_counts.total_orders) * 100).toFixed(1);
                            return (
                                <div key={index} className="flex items-center justify-between p-2 hover:bg-slate-50 rounded-lg transition-colors">
                                    <div className="flex items-center gap-2">
                                        {/* یک دایره رنگی دکوری */}
                                        <div className={`w-3 h-3 rounded-full ${status.current_status__name.includes("رد شده") ? "bg-red-500" : "bg-blue-500"}`}></div>
                                        <span className="text-sm font-bold text-slate-700">{status.current_status__name}</span>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="text-sm font-black text-slate-900">{status.count}</span>
                                        <span className="text-xs text-slate-400 w-8 text-left">{percentage}٪</span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>

        {/* 4. ENTITY COUNTS (آمار کلی - ستون چپ) */}
        <div className="xl:col-span-4 space-y-6">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 h-full">
                <h2 className="text-lg font-black text-slate-800 mb-6 flex items-center gap-2">
                    <BarChart4 className="h-5 w-5 text-gold-dark" />
                    شاخص‌های عملیاتی
                </h2>
                
                <div className="space-y-4">
                    <MiniStatCard 
                        icon={<ShoppingBag className="h-5 w-5 text-blue-600" />}
                        title="سفارشات این ماه"
                        value={entity_counts.total_orders_month}
                        bgColor="bg-blue-50"
                    />
                    <MiniStatCard 
                        icon={<Briefcase className="h-5 w-5 text-emerald-600" />}
                        title="کل سفارشات سیستم"
                        value={entity_counts.total_orders}
                        bgColor="bg-emerald-50"
                    />
                    <div className="my-4"><hr className="border-dashed border-slate-200" /></div>
                    <MiniStatCard 
                        icon={<Users className="h-5 w-5 text-purple-600" />}
                        title="مشتریان ثبت‌نامی"
                        value={entity_counts.total_customers}
                        bgColor="bg-purple-50"
                    />
                    <MiniStatCard 
                        icon={<Users className="h-5 w-5 text-slate-600" />}
                        title="پرسنل و کارمندان"
                        value={entity_counts.total_staff}
                        bgColor="bg-slate-100"
                    />
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};

// --- کامپوننت‌های فرعی (استایل‌های کارت‌ها) ---

const KpiCard = ({ title, value, unit, subtitle, icon, colorClass, valueColor }) => (
    <div className={`bg-white rounded-2xl border shadow-sm p-6 relative overflow-hidden transition-all hover:shadow-md ${colorClass}`}>
        <div className="flex justify-between items-start mb-4">
            <h3 className="text-sm font-bold text-slate-600">{title}</h3>
            <div className="p-2 bg-white rounded-lg shadow-sm">{icon}</div>
        </div>
        <div className="flex items-baseline gap-1">
            <span className={`text-3xl font-black tracking-tight ${valueColor}`}>{value}</span>
            {unit && <span className="text-xs font-bold text-slate-400 mb-1">{unit}</span>}
        </div>
        <p className="text-xs text-slate-500 mt-2 font-medium">{subtitle}</p>
    </div>
);

const MiniStatCard = ({ icon, title, value, bgColor }) => (
    <div className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
        <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl ${bgColor}`}>{icon}</div>
            <span className="font-bold text-slate-700 text-sm">{title}</span>
        </div>
        <span className="text-xl font-black text-slate-900">{value}</span>
    </div>
);

// --- اسکلتون لودینگ ---
const DashboardSkeleton = () => (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
        <div className="h-32 bg-slate-200 rounded-2xl animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 bg-slate-200 rounded-2xl animate-pulse"></div>
            <div className="h-32 bg-slate-200 rounded-2xl animate-pulse"></div>
            <div className="h-32 bg-slate-200 rounded-2xl animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
            <div className="xl:col-span-8 h-[400px] bg-slate-200 rounded-2xl animate-pulse"></div>
            <div className="xl:col-span-4 h-[400px] bg-slate-200 rounded-2xl animate-pulse"></div>
        </div>
    </div>
);

export default AdminDashboard;