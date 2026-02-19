import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check, X, Eye } from "lucide-react";
import { Link } from "react-router-dom";

export const getDesignColumns = (onApprove, onReject) => [
  {
    accessorKey: "order_code",
    header: "شناسه",
    cell: ({ row }) => <span className="font-mono text-[11px] font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-sm border border-slate-200">{row.getValue("order_code")}</span>
  },
  {
    accessorKey: "recipient_name",
    header: "مشتری",
    cell: ({ row }) => (
      <div className="flex flex-col">
        <span className="font-bold text-sm text-slate-800">{row.getValue("recipient_name")}</span>
        <span className="text-[10px] text-slate-500">{row.original.company_name}</span>
      </div>
    )
  },
  {
    accessorKey: "current_status_display",
    header: "وضعیت",
    cell: ({ row }) => <Badge variant="outline" className="text-[10px] font-medium">{row.getValue("current_status_display")}</Badge>
  },
  {
    id: "actions",
    header: "عملیات طراح",
    // ⭐️ اینجا با meta عرض ستون را برای طراح کاستوم کردیم
    meta: { className: "w-[250px] min-w-[250px] justify-center" }, 
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <Link to={`/designer/orders/detail/${row.original.id}`}>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0"><Eye size={14}/></Button>
        </Link>
        <Button 
          size="sm" 
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] h-8 px-3"
          onClick={() => onApprove(row.original.id)}
        >
          <Check size={14} className="ml-1" /> تایید طراحی
        </Button>
        <Button 
          variant="destructive" 
          size="sm" 
          className="text-[10px] h-8 px-3"
          onClick={() => {
            const reason = window.prompt("دلیل رد فایل چیست؟");
            if (reason) onReject({ id: row.original.id, description: reason });
          }}
        >
          <X size={14} className="ml-1" /> رد فایل
        </Button>
      </div>
    )
  }
];