import React from "react";
import { useParams } from "react-router-dom";

export default function LogisticsOrderDetail() {
  const { id } = useParams();
  return (
    <div className="space-y-4">
        <h2 className="text-xl font-bold">اطلاعات ارسال - سفارش #{id}</h2>
        <div className="grid gap-4">
            <div className="p-4 border rounded">آدرس گیرنده و لوکیشن</div>
            <div className="p-4 border rounded">فرم ثبت هزینه پیک</div>
        </div>
    </div>
  );
}