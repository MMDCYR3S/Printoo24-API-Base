import React from "react";
import { OrdersDataTable } from "../components/OrdersDataTable";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function OrdersPage() {
  return (
    <div className="flex-1 space-y-6 p-8 pt-6 animate-in fade-in duration-500">
      {/* هدر صفحه */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-gray-dark">مدیریت سفارشات</h2>
          <p className="text-gray-500 mt-1">
            لیست تمام سفارشات جاری، در انتظار تایید و تکمیل شده.
          </p>
        </div>
        
        {/* دکمه اصلی ایجاد سفارش: طلایی با متن تیره */}
        <Button className="bg-primary text-primary-foreground hover:bg-gold-dark shadow-lg shadow-primary/20 transition-all font-bold">
          <Plus className="ml-2 h-4 w-4" />
          ثبت سفارش جدید
        </Button>
      </div>

      {/* جداکننده گرافیکی کوچک */}
      <div className="h-1 w-24 bg-gradient-to-l from-primary to-transparent rounded-full opacity-50"></div>

      {/* جدول */}
      <OrdersDataTable />
    </div>
  );
}