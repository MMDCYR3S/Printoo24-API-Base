import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { MoreHorizontal, Edit, Trash2, Shield, UserCog, Clock } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuLabel } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const getInitials = (username) => {
    return username ? username.substring(0, 2).toUpperCase() : "U";
};

export const getStaffColumns = (onEdit, onDelete) => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        className="rounded-[4px] border-slate-400 data-[state=checked]:bg-gold-dark"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        className="rounded-[4px] border-slate-300 data-[state=checked]:bg-gold-dark"
      />
    ),
  },
  {
    accessorKey: "username",
    header: "کارمند",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <Avatar className="h-9 w-9 border border-slate-200 rounded-md bg-slate-100">
            <AvatarFallback className="text-slate-600 text-xs font-bold">
                {getInitials(row.original.username)}
            </AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
            <span className="font-bold text-sm text-slate-800">{row.original.username}</span>
            <span className="text-[10px] text-slate-400 font-mono">{row.original.email}</span>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "role_name",
    header: "نقش سازمانی",
    cell: ({ row }) => (
        <div className="flex items-center gap-1.5 bg-blue-50 text-blue-700 px-2.5 py-1 rounded-sm border border-blue-100 w-fit">
            <Shield size={12} />
            <span className="text-xs font-bold">{row.original.role_name || "تعیین نشده"}</span>
        </div>
    ),
  },
  {
    accessorKey: "is_active",
    header: "وضعیت",
    cell: ({ row }) => (
        <Badge variant="outline" className={`rounded-sm text-[10px] px-2 h-5 border-0 ${row.original.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
            {row.original.is_active ? "فعال" : "غیرفعال"}
        </Badge>
    ),
  },
  {
    accessorKey: "last_login",
    header: "آخرین ورود",
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5 text-xs text-slate-500">
        <Clock size={12} />
        {row.original.last_login 
            ? new Date(row.original.last_login).toLocaleDateString('fa-IR') 
            : "---"}
      </div>
    ),
  },
  {
    id: "actions",
    cell: ({ row }) => (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-slate-100">
            <MoreHorizontal className="h-4 w-4 text-slate-400" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-40 border-slate-100">
          <DropdownMenuLabel className="text-[10px] text-slate-400">مدیریت پرسنل</DropdownMenuLabel>
          <DropdownMenuItem onClick={() => onEdit(row.original)} className="text-xs cursor-pointer gap-2">
            <Edit className="h-3.5 w-3.5" /> ویرایش دسترسی
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => onDelete(row.original.id)} className="text-xs cursor-pointer text-red-600 gap-2">
            <Trash2 className="h-3.5 w-3.5" /> اخراج کارمند
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    ),
  },
];