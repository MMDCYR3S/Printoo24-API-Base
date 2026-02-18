// مسیر: src/features/roles/admin/config/adminNavigation.js
import { 
  LayoutDashboard, PlusCircle, ShoppingCart, Users, UserPlus,
  PenTool, Printer, Package, Banknote 
} from "lucide-react";

export const adminNavigation = [
  {
    id: "management",
    title: "پنل مدیریت",
    items: [
      { title: "داشبورد", icon: LayoutDashboard, href: "/admin/adminDashboard" },
      { title: "سفارش جدید", icon: PlusCircle, href: "/admin/orders/new" },
      { title: "همه سفارش‌ها", icon: ShoppingCart, href: "/admin/orders" },
      { title: "مدیریت کارمندان", icon: Users, href: "/admin/users/staff" },
      { title: "مدیریت مشتریان", icon: UserPlus, href: "/admin/customers" },
    ]
  },
  {
    id: "shortcuts",
    title: "دسترسی سریع",
    items: [
      { title: "طراح", icon: PenTool, href: "/design/designDashboard" },
      { title: "چاپ", icon: Printer, href: "/print/printDashboard" },
      { title: "انبار", icon: Package, href: "/logistics/logisticsDashboard" },
      { title: "مالی", icon: Banknote, href: "/financial/financialDashboard" },
    ]
  }
];