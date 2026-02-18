import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

// تعریف رنگ‌های اختصاصی برای وضعیت‌های مختلف (تم صنعتی)
const COLORS = {
  "در انتظار بررسی": "#f59e0b", // Amber (Gold)
  "در حال طراحی": "#3b82f6", // Blue
  "در حال چاپ": "#6366f1", // Indigo
  "دریافت توسط انبار": "#10b981", // Emerald
  "ارسال به انبار": "#0ea5e9", // Sky
  "تحویل‌شده": "#059669", // Emerald Dark
  "لغو شده": "#64748b", // Slate
  "رد شده توسط طراح": "#ef4444", // Red
  "رد شده توسط چاپ": "#ef4444", // Red
  "رد شده توسط انبار": "#ef4444", // Red
  "DEFAULT": "#cbd5e1"
};

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 text-white p-3 rounded-md shadow-xl border border-slate-700 text-xs font-mono dir-rtl">
        <p className="font-bold mb-1">{payload[0].name}</p>
        <p className="text-gold-light">{payload[0].value} سفارش</p>
      </div>
    );
  }
  return null;
};

const StatusDonutChart = ({ data }) => {
  // تبدیل دیتای بک‌ند به فرمت Recharts
  const chartData = data.map(item => ({
    name: item.current_status__name,
    value: item.count
  }));

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={80}
            outerRadius={110}
            paddingAngle={4}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={COLORS[entry.name] || COLORS["DEFAULT"]} 
                className="hover:opacity-80 transition-opacity outline-none"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
             verticalAlign="bottom" 
             height={36} 
             iconType="circle"
             wrapperStyle={{ fontSize: '11px', fontWeight: 'bold', color: '#475569' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StatusDonutChart;