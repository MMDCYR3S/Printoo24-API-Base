import { MoreHorizontal, ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// تابع کمکی برای فرمت قیمت (ریال)
const formatPrice = (price) => {
  return new Intl.NumberFormat("fa-IR", {
    style: "currency",
    currency: "IRR",
  }).format(price);
};

// تعریف ستون‌ها برای TanStack Table
export const columns = [
  {
    accessorKey: "order_code", // کلید در دیتای جیسون [cite: 106]
    header: "کد سفارش",
  },
  {
    accessorKey: "company_name", // [cite: 105]
    header: "نام شرکت/مشتری",
  },
  {
    accessorKey: "recipient_name", // [cite: 103]
    header: "تحویل گیرنده",
  },
  {
    accessorKey: "created_at", // [cite: 107]
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          تاریخ ثبت
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      // اینجا می‌توانیم از کتابخانه date-fns-jalali برای تبدیل تاریخ استفاده کنیم
      const date = new Date(row.getValue("created_at"));
      return <div className="text-right font-medium">{date.toLocaleDateString("fa-IR")}</div>;
    },
  },
  {
    accessorKey: "total_price", // [cite: 117]
    header: "مبلغ کل",
    cell: ({ row }) => {
      const price = parseFloat(row.getValue("total_price") || 0);
      return <div className="font-medium">{formatPrice(price)}</div>;
    },
  },
  {
    accessorKey: "current_status_display", // [cite: 109]
    header: "وضعیت",
    cell: ({ row }) => {
      const status = row.getValue("current_status_display");
      // استایل دهی شرطی بر اساس متن وضعیت
      let colorClass = "bg-gray-100 text-gray-800";
      
      if (status.includes("تایید")) colorClass = "bg-green-100 text-green-800";
      if (status.includes("بررسی")) colorClass = "bg-yellow-100 text-yellow-800";
      if (status.includes("چاپ")) colorClass = "bg-blue-100 text-blue-800";

      return (
        <span className={`px-2 py-1 rounded-full text-xs font-bold ${colorClass}`}>
          {status}
        </span>
      );
    },
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const order = row.original;
 
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">منو</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>عملیات</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(order.order_code)}
            >
              کپی کد سفارش
            </DropdownMenuItem>
            <DropdownMenuItem>مشاهده جزئیات</DropdownMenuItem>
            <DropdownMenuItem className="text-red-600">حذف سفارش</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];