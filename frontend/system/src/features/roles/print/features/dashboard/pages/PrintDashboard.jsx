import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function PrintDashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-purple-600">صف چاپ</h2>
      <div className="p-4 border rounded-lg bg-white shadow-sm">
          <p className="mb-4">سفارشات آماده چاپ:</p>
          <Link to="/orders/detail/880"><Button className="bg-purple-600 hover:bg-purple-700">چاپ سفارش #880</Button></Link>
      </div>
    </div>
  );
}