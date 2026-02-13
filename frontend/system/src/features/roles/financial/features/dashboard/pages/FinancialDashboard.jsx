import React from "react";

export default function FinancialDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-emerald-600">مانیتورینگ مالی</h2>
      <div className="grid gap-4 md:grid-cols-3">
          <div className="p-6 bg-emerald-50 text-emerald-900 rounded-lg">درآمد کل: 50.000.000</div>
          <div className="p-6 bg-red-50 text-red-900 rounded-lg">هزینه کل: 12.000.000</div>
          <div className="p-6 bg-white border border-emerald-200 rounded-lg shadow-sm font-bold">سود خالص: 38.000.000</div>
      </div>
      <div className="h-96 bg-gray-50 border rounded flex items-center justify-center">
          جدول لایو سفارشات (Live Monitor)
      </div>
    </div>
  );
}