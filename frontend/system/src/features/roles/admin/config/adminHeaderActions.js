import { UserPlus, PlusSquare } from "lucide-react";

export const adminHeaderActions = [
  {
    title: "افزودن سفارش",
    icon: PlusSquare,
    href: "/orders/new", // یا اکشن مودال
    variant: "primary"
  },
  {
    title: "افزودن مشتری",
    icon: UserPlus,
    href: "/users/customers/new",
    variant: "primary"
  }
];