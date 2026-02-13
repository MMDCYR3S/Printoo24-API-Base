import React from "react";
import { useParams } from "react-router-dom";

export default function PrintOrderDetail() {
  const { id } = useParams();
  return (
    <div className="space-y-4">
        <h2 className="text-xl font-bold">جزئیات چاپ - سفارش #{id}</h2>
        <div className="p-6 border rounded bg-purple-50">
            فرم ثبت هزینه‌های متریال و چاپ
        </div>
    </div>
  );
}