import { MoreHorizontal, ArrowUpDown, Copy, Eye, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge"; // حالا این فایل وجود دارد
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

// فرمت پول به ریال
const formatCurrency = (amount) => {
  if (!amount) return "۰ ریال";
  return new Intl.NumberFormat("fa-IR", {
    style: "currency",
    currency: "IRR",
    maximumFractionDigits: 0,
  }).format(amount);
};

// فرمت تاریخ به شمسی
const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Intl.DateTimeFormat("fa-IR", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(dateString));
};

export const columns = [
  {
    accessorKey: "order_code",
    header: "کد سفارش",
    cell: ({ row }) => (
      <div className="font-mono text-xs font-bold text-gray-600 bg-gray-100 px-2 py-1 rounded-md inline-block tracking-wider border border-gray-200">
        {row.getValue("order_code")}
      </div>
    ),
  },
  {
    accessorKey: "company_name",
    header: "مشتری / شرکت",
    cell: ({ row }) => {
      const company = row.getValue("company_name");
      const recipient = row.original.recipient_name;
      return (
        <div className="flex flex-col">
          <span className="font-bold text-gray-800 text-sm">{company || recipient}</span>
          {company && <span className="text-xs text-gray-500">{recipient}</span>}
        </div>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          className="text-gold-light hover:text-white p-0 hover:bg-transparent"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          تاریخ ثبت
          <ArrowUpDown className="mr-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="text-sm text-gray-600 font-medium">{formatDate(row.getValue("created_at"))}</div>
    ),
  },
  {
    accessorKey: "total_price",
    header: "مبلغ کل",
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue("total_price"));
      return <div className="font-bold text-gray-800">{formatCurrency(amount)}</div>;
    },
  },
  {
    accessorKey: "items_count",
    header: "اقلام",
    cell: ({ row }) => (
      <div className="flex justify-center">
         <span className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-50 text-xs font-bold text-gray-700 border border-gray-200 shadow-sm">
            {row.getValue("items_count") || 0}
         </span>
      </div>
    ),
  },
  {
    accessorKey: "current_status_display",
    header: "وضعیت",
    cell: ({ row }) => {
      const status = row.getValue("current_status_display") || "نامشخص";
      const isLocked = row.original.is_locked;

      // انتخاب واریانت مناسب برای Badge
      let variant = "neutral";
      if (status.includes("تایید") || status.includes("آماده")) variant = "success";
      else if (status.includes("چاپ") || status.includes("اجرا")) variant = "info";
      else if (status.includes("مالی") || status.includes("پرداخت")) variant = "warning";
      else if (status.includes("لغو") || isLocked) variant = "destructive";

      return (
        <Badge variant={variant} className="gap-1 font-medium shadow-sm">
          {isLocked && <span>🔒</span>}
          {status}
        </Badge>
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
            <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-gold-light/20 text-gray-500">
              <span className="sr-only">منو</span>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>عملیات سفارش</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(order.order_code)}
              className="cursor-pointer"
            >
              <Copy className="ml-2 h-4 w-4 text-gray-400" />
              کپی کد سفارش
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer font-medium text-gray-700">
              <Eye className="ml-2 h-4 w-4 text-blue-500" />
              مشاهده جزئیات
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <FileText className="ml-2 h-4 w-4 text-gold-dark" />
              فاکتور فروش
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];