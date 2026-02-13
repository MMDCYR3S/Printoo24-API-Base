import React from "react";
import { useParams } from "react-router-dom";
export default function FinancialOrderDetail() {
  const { id } = useParams();
  return <div className="p-6 border rounded">صورت حساب کامل سفارش #{id}</div>;
}