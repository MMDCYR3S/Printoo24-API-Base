import React from "react";
import OrdersDataTable from "@/features/shared/orders/components/OrdersDataTable";
import { useDesignOrders } from "../../../hooks/useDesignOrders";
import { getDesignColumns } from "../components/designColumns";

export default function DesignOrderList() {
  const { orders, isLoading, approve, reject } = useDesignOrders();
  
  // تولید ستون‌ها با تزریق اکشن‌های تایید و رد
  const columns = getDesignColumns(approve, reject);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-black text-slate-800">کارتابل طراحی</h1>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-slate-100">
        <OrdersDataTable 
          data={orders} 
          isLoading={isLoading} 
          columns={columns} 
        />
      </div>
    </div>
  );
}