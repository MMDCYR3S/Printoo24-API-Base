import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { MoreHorizontal, Edit, Trash2, Phone, Building2, UserCheck, UserX } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuLabel } from "@/components/ui/dropdown-menu";

const getInitials = (first, last) => {
    const f = first ? first[0] : "";
    const l = last ? last[0] : "";
    return (f + l).toUpperCase() || "U";
};

export const getCustomerColumns = (onEdit, onDelete) => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        className="rounded-[4px] border-slate-400 data-[state=checked]:bg-gold-dark data-[state=checked]:border-gold-dark"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        className="rounded-[4px] border-slate-300 data-[state=checked]:bg-gold-dark data-[state=checked]:border-gold-dark"
      />
    ),
  },
  {
    accessorKey: "full_name",
    header: "نام و نام خانوادگی",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <Avatar className="h-9 w-9 border border-slate-200 rounded-md">
            <AvatarFallback className="bg-slate-100 text-slate-600 text-xs font-bold rounded-md">
                {getInitials(row.original.first_name, row.original.last_name)}
            </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
            <span className="font-bold text-sm text-slate-800">
                {row.original.first_name} {row.original.last_name}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">@{row.original.username}</span>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "company",
    header: "شرکت",
    cell: ({ row }) => (
        row.getValue("company") ? (
            <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-slate-50 px-2 py-1 rounded-sm border border-slate-100 w-fit">
                <Building2 size={12} className="text-slate-400" />
                {row.getValue("company")}
            </div>
        ) : <span className="text-slate-300 text-xs">-</span>
    ),
  },
  {
    accessorKey: "phone_number",
    header: "شماره تماس",
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-slate-50 px-2 py-1 rounded-sm border border-slate-100 w-fit">
        <Phone size={12} className="text-slate-400" />
        <span dir="ltr" className="font-mono tracking-wide">{row.getValue("phone_number")}</span>
      </div>
    ),
  },
  {
    accessorKey: "is_active",
    header: "وضعیت",
    cell: ({ row }) => (
        <Badge variant="outline" className={`rounded-sm text-[10px] px-2 h-5 gap-1 ${row.original.is_active ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'}`}>
            {row.original.is_active ? <UserCheck size={10} /> : <UserX size={10} />}
            {row.original.is_active ? "فعال" : "غیرفعال"}
        </Badge>
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-700">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-40 shadow-xl border-slate-100 rounded-md p-1">
          <DropdownMenuLabel className="text-[10px] text-slate-400 px-2 py-1.5">عملیات</DropdownMenuLabel>
          <DropdownMenuItem onClick={() => onEdit(row.original)} className="rounded-sm text-xs cursor-pointer gap-2">
            <Edit className="h-3.5 w-3.5 text-slate-500" /> ویرایش
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => onDelete(row.original.id)} className="rounded-sm text-xs cursor-pointer text-red-600 gap-2">
            <Trash2 className="h-3.5 w-3.5" /> حذف
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
  },
];