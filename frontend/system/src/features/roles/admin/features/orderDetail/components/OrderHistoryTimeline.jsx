import React from "react";
import { useQuery } from "@tanstack/react-query";
import { orderService } from "@/features/shared/orders/api/orderService";
import { AlertCircle, History, ArrowDownCircle, UserCircle2, MessageSquareText } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
// import { format } from "date-fns-jalali";

const OrderHistoryTimeline = ({ orderId }) => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["orderHistory", orderId],
    queryFn: () => orderService.getOrderHistory(orderId),
  });

  if (isLoading) return <TimelineSkeleton />;

  if (isError) return (
    <div className="bg-rose-50 text-rose-500 p-4 rounded-xl flex items-center gap-3 text-sm">
      <AlertCircle className="h-5 w-5" />
      <p>خطا در بارگذاری تاریخچه سفارش.</p>
    </div>
  );

  const logs = data?.logs || [];

  if (logs.length === 0) return (
    <div className="bg-slate-50 border border-slate-100 p-6 rounded-xl flex flex-col items-center justify-center text-slate-400 gap-2">
      <History className="h-8 w-8 mb-1 opacity-50" />
      <p className="text-sm font-medium">تاریخچه‌ای برای این سفارش ثبت نشده است.</p>
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      <div className="px-6 py-5 border-b border-slate-100 flex items-center gap-3 bg-slate-50/50">
        <div className="bg-blue-100 p-2 rounded-lg text-blue-600">
          <History className="h-5 w-5" />
        </div>
        <div>
          <h2 className="font-bold text-slate-800 text-lg">تاریخچه وضعیت سفارش</h2>
          <p className="text-xs text-slate-500 mt-0.5">وضعیت فعلی: <span className="font-bold text-slate-700">{data.current_status}</span></p>
        </div>
      </div>

      <div className="p-6 relative">
        {/* خط عمودی تایم لاین */}
        <div className="absolute top-10 bottom-10 right-[39px] w-0.5 bg-slate-100"></div>

        <div className="space-y-6 relative z-10">
          {logs.map((log, index) => {
            // تشخیص رنگ بر اساس کلمه "رد شده"
            const isRejected = log.to_status_title.includes("رد");
            const badgeColor = isRejected ? "bg-rose-100 text-rose-700 border-rose-200" : "bg-emerald-100 text-emerald-700 border-emerald-200";
            const iconColor = isRejected ? "text-rose-500" : "text-emerald-500";

            return (
              <div key={log.id} className="flex gap-4 items-start group">
                <div className={`mt-1 bg-white border-2 border-slate-200 rounded-full p-1 transition-colors group-hover:border-blue-400`}>
                  <ArrowDownCircle className={`h-4 w-4 ${iconColor}`} />
                </div>
                
                <div className="flex-1 bg-slate-50 border border-slate-100 rounded-xl p-4 hover:shadow-md transition-all">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-medium text-slate-500 line-through decoration-slate-300">{log.from_status_title}</span>
                      <span className="text-slate-400 text-xs">➔</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded border ${badgeColor}`}>
                        {log.to_status_title}
                      </span>
                    </div>
                    
<div className="text-[11px] font-mono text-slate-400 flex flex-col sm:items-end">
  <span>{new Date(log.created_at).toLocaleDateString('fa-IR', { year: 'numeric', month: '2-digit', day: '2-digit' })}</span>
  <span>{new Date(log.created_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
</div>
                  </div>

                  <div className="flex flex-col gap-2 mt-3 pt-3 border-t border-slate-200/60">
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <UserCircle2 className="h-4 w-4 text-slate-400" />
                      <span className="font-medium text-slate-700">تغییر توسط:</span> 
                      <span className="font-bold text-blue-600 uppercase">{log.actor_name}</span>
                    </div>
                    
                    {log.description && (
                      <div className="flex items-start gap-2 text-sm text-slate-600 bg-white p-3 rounded-lg border border-slate-100">
                        <MessageSquareText className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
                        <p className="leading-relaxed text-slate-700 text-justify">{log.description}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const TimelineSkeleton = () => (
  <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-6">
    <Skeleton className="h-8 w-1/3 mb-6" />
    {[1, 2, 3].map((i) => (
      <div key={i} className="flex gap-4">
        <Skeleton className="h-6 w-6 rounded-full shrink-0" />
        <Skeleton className="h-28 w-full rounded-xl" />
      </div>
    ))}
  </div>
);

export default OrderHistoryTimeline;