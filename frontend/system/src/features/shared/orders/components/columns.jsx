import { MoreHorizontal, ArrowUpDown, Copy, Eye, FileText, CheckCircle2, XCircle, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

// فرمت پول به تومان (رندومایز شده طبق مثال بک‌ند)
const formatCurrency = (amount) => {
  if (!amount) return "۰ تومان";
  return new Intl.NumberFormat("fa-IR").format(amount) + " تومان";
};

// فرمت تاریخ و ساعت (ساعت در چاپخانه مهم است)
const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Intl.DateTimeFormat("fa-IR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateString));
};

export const getColumns = (handleApprove, handleReject) => [
  {
    accessorKey: "order_code",
    header: "شناسه",
    cell: ({ row }) => (
      <div className="font-mono text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-100">
        {row.getValue("order_code")}
      </div>
    ),
  },
  {
    accessorKey: "recipient_name",
    header: "مشتری / تحویل‌گیرنده",
    cell: ({ row }) => {
      const company = row.original.company_name;
      const recipient = row.original.recipient_name;
      const phone = row.original.recipient_phone;
      return (
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-gray-900 text-sm">{company || recipient}</span>
            {row.original.type_display === "اختصاصی" && (
              <Badge variant="outline" className="text-[9px] h-4 px-1 border-amber-200 text-amber-700 bg-amber-50">اختصاصی</Badge>
            )}
          </div>
          <div className="flex items-center text-[11px] text-gray-500 gap-1">
            <Phone size={10} />
            <span className="font-mono">{phone}</span>
          </div>
        </div>
      );
    },
  },
  {
    accessorKey: "total_price",
    header: "مبلغ کل",
    cell: ({ row }) => <div className="font-bold text-gray-800 text-sm">{formatCurrency(row.getValue("total_price"))}</div>,
  },
  {
    accessorKey: "items_count",
    header: "اقلام",
    cell: ({ row }) => (
      <div className="text-center">
        <span className="inline-flex items-center justify-center w-6 h-6 rounded bg-gray-100 text-[11px] font-bold border">
          {row.getValue("items_count")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "created_at",
    header: "زمان ثبت",
    cell: ({ row }) => (
      <div className="text-[11px] text-gray-500 leading-tight">
        {formatDate(row.getValue("created_at"))}
      </div>
    ),
  },
  {
    accessorKey: "status_display",
    header: "وضعیت فعلی",
    cell: ({ row }) => {
      const status = row.original.status_display || "نامشخص";
      const isLocked = row.original.is_locked;

      let badgeClass = "bg-gray-100 text-gray-600 border-gray-200";
      if (status.includes("تایید")) badgeClass = "bg-green-50 text-green-700 border-green-200";
      if (status.includes("چاپ") || status.includes("تولید")) badgeClass = "bg-purple-50 text-purple-700 border-purple-200";
      if (status.includes("طراحی")) badgeClass = "bg-blue-50 text-blue-700 border-blue-200";
      if (status.includes("ارسال") || status.includes("پیک")) badgeClass = "bg-amber-50 text-amber-700 border-amber-200";

      return (
        <Badge className={`font-medium shadow-none border ${badgeClass} gap-1`}>
          {isLocked && <span className="text-[10px]">🔒</span>}
          {status}
        </Badge>
      );
    },
  },
  {
    id: "quick_actions",
    header: "عملیات سریع",
    cell: ({ row }) => {
      const id = row.original.id;
      return (
        <div className="flex items-center gap-1">
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-8 w-8 p-0 text-green-600 hover:text-green-700 hover:bg-green-50"
            onClick={() => handleApprove(id)}
            title="تایید و مرحله بعد"
          >
            <CheckCircle2 className="h-4 w-4" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-8 w-8 p-0 text-red-500 hover:text-red-600 hover:bg-red-50"
            onClick={() => handleReject(id)}
            title="رد / لغو"
          >
            <XCircle className="h-4 w-4" />
          </Button>
        </div>
      );
    }
  },
  {
    id: "more",
    cell: ({ row }) => {
      const order = row.original;
      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-40">
            <DropdownMenuItem onClick={() => {
               navigator.clipboard.writeText(order.order_code);
               toast.success("کد سفارش کپی شد");
            }}>
              <Copy className="ml-2 h-4 w-4" /> کپی کد
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-blue-600">
              <Eye className="ml-2 h-4 w-4" /> مشاهده جزئیات
            </DropdownMenuItem>
            <DropdownMenuItem>
              <FileText className="ml-2 h-4 w-4" /> چاپ فاکتور
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];