import React from "react";
import { OrdersDataTable } from "../components/OrdersDataTable";
import { columns } from "../components/columns"; // ستون‌هایی که قبلا ساختیم

export default function OrdersPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">مدیریت سفارشات</h2>
        <div className="flex items-center space-x-2">
          {/* دکمه دانلود یا اکشن‌های هدر اینجا می‌آیند */}
        </div>
      </div>
      <div className="hidden h-full flex-1 flex-col space-y-8 md:flex">
        {/* پاس دادن ستون‌ها و دیتا به جدول */}
        <OrdersDataTable columns={columns} />
      </div>
    </div>
  );
}