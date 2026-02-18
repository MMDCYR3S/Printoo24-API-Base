import { LayoutDashboard, ListOrdered, DollarSign, Clock } from "lucide-react";

export const financialNavigation = [
  {
    title: "داشبورد مالی",
    href: "/financial/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "سفارشات",
    href: "/financial/orders",
    icon: ListOrdered,
  },
  {
    title: "تراکنش‌های در انتظار",
    href: "/financial/pending-transactions",
    icon: Clock,
  },
  {
    title: "تراکنش‌ها",
    href: "/financial/transactions",
    icon: DollarSign,
  },
];