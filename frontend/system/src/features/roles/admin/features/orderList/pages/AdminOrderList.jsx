import React from "react";
import { useOrders } from "@/features/shared/orders/hooks/useOrders";
import OrdersDataTable from "@/features/shared/orders/components/OrdersDataTable";
import { Button } from "@/components/ui/button";
import { Plus, RefreshCcw, LayoutDashboard } from "lucide-react";
import { useNavigate } from "react-router-dom";

const AdminOrderList = () => {
  const navigate = useNavigate();
  
  // ۱. دریافت دیتا با استفاده از هوک TanStack Query
  // ما اینجا پارامترهای فیلتر اولیه (مثل پجینیشن) رو هم میتونیم پاس بدیم
  const { data, isLoading, isError, refetch, isFetching } = useOrders();

  return (
    <div className="p-6 space-y-6">
      {/* هدر صفحه کارتابل */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <LayoutDashboard className="text-blue-600" />
            کارتابل جامع سفارشات
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            مدیریت، تایید و پیگیری تمام سفارشات ورودی سیستم
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* دکمه رفرش لیست */}
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()} 
            disabled={isFetching}
            className="gap-2"
          >
            <RefreshCcw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            بروزرسانی
          </Button>

          {/* دکمه انتقال به صفحه ثبت سفارش که قبلا ساختیم */}
          <Button 
            onClick={() => navigate("/admin/orders/create")} 
            className="gap-2 bg-blue-600 hover:bg-blue-700 shadow-md"
          >
            <Plus className="h-4 w-4" />
            ثبت سفارش جدید
          </Button>
        </div>
      </div>

      {/* ۲. بدنه اصلی صفحه: جدول سفارشات */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        {isError ? (
          <div className="p-12 text-center space-y-4">
            <div className="text-red-500 font-bold">خطا در دریافت اطلاعات از سرور!</div>
            <Button variant="link" onClick={() => refetch()}>تلاش مجدد</Button>
          </div>
        ) : (
          <OrdersDataTable 
            data={data || []} 
            isLoading={isLoading} 
          />
        )}
      </div>

      {/* راهنمای سریع وضعیت‌ها برای ادمین */}
      <div className="flex flex-wrap gap-4 text-[11px] text-gray-400 mt-4 bg-gray-50 p-3 rounded-lg border border-dashed">
        <span className="font-bold">راهنمای وضعیت:</span>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div> طراحی
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-purple-500"></div> چاپ و تولید
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-green-500"></div> آماده تحویل
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-amber-500"></div> در حال ارسال
        </div>
      </div>
    </div>
  );
};

export default AdminOrderList;