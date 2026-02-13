import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function LogisticsDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-orange-600">مدیریت لجستیک و انبار</h2>
      <div className="p-4 bg-orange-50 border border-orange-200 rounded">
          <h3 className="font-bold mb-2">آماده ارسال</h3>
          <Link to="/orders/detail/900"><Button variant="outline" className="border-orange-400 text-orange-600">ارسال سفارش #900</Button></Link>
      </div>
    </div>
  );
}