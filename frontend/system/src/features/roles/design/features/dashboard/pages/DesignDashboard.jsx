import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function DesignDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-blue-600">کارتابل طراحی</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="p-6 bg-blue-50 rounded-lg border border-blue-100">
            <h3 className="font-bold">منتظر طراحی</h3>
            <p className="text-3xl mt-2">5</p>
        </div>
      </div>
      <div className="mt-8">
          <h4 className="font-bold mb-4">وظایف من:</h4>
          <Link to="/orders/detail/505"><Button variant="secondary">طراحی سفارش #505</Button></Link>
      </div>
    </div>
  );
}