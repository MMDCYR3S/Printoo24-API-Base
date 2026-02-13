import React from "react";
import { useParams } from "react-router-dom";

export default function OrderDetail() {
  const { id } = useParams(); // گرفتن ID از URL

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <div>
            <h2 className="text-2xl font-bold">جزئیات سفارش #{id}</h2>
            <p className="text-gray-500 text-sm">وضعیت: در حال بررسی</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 border rounded bg-gray-50">بخش اطلاعات مشتری</div>
          <div className="p-4 border rounded bg-gray-50">بخش فایل‌ها و پیوست‌ها</div>
      </div>
    </div>
  );
}