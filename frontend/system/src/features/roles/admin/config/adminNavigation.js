import { 
  LayoutDashboard, 
  PlusCircle, 
  ShoppingCart, 
  Users, 
  UserPlus 
} from "lucide-react";

export const adminNavigation = [
  { 
    title: "داشبورد", 
    icon: LayoutDashboard, 
    href: "/dashboard" 
  },
  { 
    title: "سفارش جدید", 
    icon: PlusCircle, 
    href: "/orders/new" 
  },
  { 
    title: "همه سفارش‌ها", 
    icon: ShoppingCart, 
    href: "/orders" 
  },
  { 
    title: "مدیریت کارمندان", 
    icon: Users, 
    href: "/users/staff" 
  },
  { 
    title: "مدیریت مشتریان", 
    icon: UserPlus, 
    href: "/users/customers" 
  }
];