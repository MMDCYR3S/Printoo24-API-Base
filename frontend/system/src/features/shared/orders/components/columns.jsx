import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Copy, Eye, Trash2, Phone, Calendar, ArrowUpDown } from "lucide-react"; // ArrowUpDown اضافه شد
import StatusChangeCell from "./StatusChangeCell"; 
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator, DropdownMenuLabel } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Link } from "react-router-dom";

const getInitials = (name) => {
    if (!name) return "U";
    return name.substring(0, 2).toUpperCase();
}

export const columns = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        className="rounded-[4px] border-slate-00 data-[state=checked]:bg-gold-dark data-[state=checked]:border-gold-dark"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        className="rounded-[4px] border-slate-300 data-[state=checked]:bg-gold-dark data-[state=checked]:border-gold-dark"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "order_code",
    header: "شناسه",
    cell: ({ row }) => (
      <div className="flex items-center group cursor-pointer" onClick={() => navigator.clipboard.writeText(row.getValue("order_code"))}>
        <span className="font-mono text-[11px] font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-sm border border-slate-200 group-hover:border-gold-dark/50 group-hover:text-gold-dark transition-colors">
            {row.getValue("order_code")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "recipient_name",
    header: "مشتری",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <Avatar className="h-9 w-9 border border-slate-200 rounded-md hidden md:flex"> {/* آواتار مربعی‌تر */}
            <AvatarFallback className="bg-slate-100 text-slate-600 text-xs font-bold rounded-md">
                {getInitials(row.getValue("recipient_name"))}
            </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
            <span className="font-bold text-sm text-slate-800">
                {row.getValue("recipient_name")}
            </span>
            {row.original.company_name && (
                <span className="text-[10px] text-slate-500 font-medium mt-0.5">
                    {row.original.company_name}
                </span>
            )}
        </div>
      </div>
    ),
  },
  {
    accessorKey: "recipient_phone", 
    header: "شماره تماس",
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-slate-50 px-2 py-1 rounded-sm border border-slate-100 w-fit">
        <Phone size={12} className="text-slate-400" />
        <span dir="ltr" className="font-mono tracking-wide">
             {row.getValue("recipient_phone")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "created_at",
    // 🔽 فعال کردن سورت تاریخ
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="text-xs font-bold text-slate-500 hover:text-slate-800 h-8 px-0"
        >
          تاریخ ثبت
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className="flex flex-col text-xs text-slate-500">
        <span className="font-medium flex items-center gap-1">
             <Calendar size={12} className="text-slate-400"/>
             {new Date(row.getValue("created_at")).toLocaleDateString('fa-IR')}
        </span>
        <span className="text-[10px] text-slate-300 mr-4">
             {new Date(row.getValue("created_at")).toLocaleTimeString('fa-IR', {hour: '2-digit', minute:'2-digit'})}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "total_price",
    // 🔽 فعال کردن سورت قیمت
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="text-xs font-bold text-slate-500 hover:text-slate-800 h-8 px-0"
        >
          مبلغ سفارش
          <ArrowUpDown className="ml-2 h-3 w-3" />
        </Button>
      )
    },
    cell: ({ row }) => (
      <div className="font-black text-slate-800 text-sm tracking-tight">
        {Number(row.getValue("total_price")).toLocaleString()} 
        <span className="text-[9px] font-normal text-slate-400 mr-1">تومان</span>
      </div>
    ),
  },
  {
    accessorKey: "internal_code", 
    header: "وضعیت",
    cell: ({ row }) => (
      <StatusChangeCell 
        orderId={row.original.id} 
        currentStatus={row.original.internal_code || row.original.status_display} 
      />
    ),
    // این خط برای فیلتر مولتی سلکت حیاتی است
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id));
    },
  },
{
    id: "actions",
    cell: ({ row }) => (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-all">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 shadow-xl border-slate-100 rounded-md p-1">
          <DropdownMenuLabel className="text-[10px] text-slate-400 px-2 py-1.5">مدیریت سفارش</DropdownMenuLabel>
          
          <DropdownMenuItem onClick={() => navigator.clipboard.writeText(row.original.order_code)} className="rounded-sm text-xs cursor-pointer">
            <Copy className="ml-2 h-3.5 w-3.5 text-slate-400" /> کپی شناسه
          </DropdownMenuItem>

          {/* ⭐️ لینک به صفحه جزئیات */}
          <DropdownMenuItem asChild>
            <Link 
              to={`/admin/orders/${row.original.id}`} 
              className="flex w-full items-center rounded-sm text-xs cursor-pointer font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50"
            >
              <Eye className="ml-2 h-3.5 w-3.5" /> مشاهده جزئیات
            </Link>
          </DropdownMenuItem>
          
          <DropdownMenuSeparator className="bg-slate-100" />
          
          <DropdownMenuItem className="rounded-sm text-xs cursor-pointer text-red-600 focus:text-red-700 focus:bg-red-50">
            <Trash2 className="ml-2 h-3.5 w-3.5" /> حذف سفارش
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
  },

];