import { Package, ListOrdered } from "lucide-react"; // استفاده از آیکون‌های متناسب با انبار

export const logisticsNavigation = [
  {
    title: "داشبورد انبار",
    href: "/logistics/dashboard",
    icon: Package,
  },
  {
    title: "سفارشات لجستیک",
    href: "/logistics/orders",
    icon: ListOrdered,
  },
];