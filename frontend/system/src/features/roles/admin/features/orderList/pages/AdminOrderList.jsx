import React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

export default function AdminOrderList() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">لیست سفارشات</h2>
        <Link to="/orders/new">
          <Button>سفارش جدید +</Button>
        </Link>
      </div>
      <div className="rounded-md border p-8 text-center bg-gray-50">
        <p>جدول سفارشات اینجا لود می‌شود...</p>
        <div className="mt-4 flex gap-2 justify-center">
            {/* دکمه تستی برای رفتن به جزئیات */}
            <Link to="/orders/detail/1001"><Button variant="outline">مشاهده سفارش 1001</Button></Link>
            <Link to="/orders/detail/1002"><Button variant="outline">مشاهده سفارش 1002</Button></Link>
        </div>
      </div>
    </div>
  );
}