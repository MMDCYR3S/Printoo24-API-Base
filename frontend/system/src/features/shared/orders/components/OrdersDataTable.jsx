import React from "react";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useOrders } from "../api/orderService";
import { columns } from "./columns";
import { Loader2, Search, SlidersHorizontal } from "lucide-react";

export function OrdersDataTable() {
  const { data: orders = [], isLoading, isError } = useOrders();
  const [sorting, setSorting] = React.useState([]);
  const [globalFilter, setGlobalFilter] = React.useState("");

  const table = useReactTable({
    data: orders,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      globalFilter,
    },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: (row, columnId, filterValue) => {
      // سرچ سفارشی روی نام مشتری و کد سفارش
      const search = filterValue.toLowerCase();
      const code = String(row.original.order_code || "").toLowerCase();
      const company = String(row.original.company_name || "").toLowerCase();
      const recipient = String(row.original.recipient_name || "").toLowerCase();
      return code.includes(search) || company.includes(search) || recipient.includes(search);
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-64 w-full items-center justify-center rounded-xl border bg-white shadow-sm">
        <div className="flex flex-col items-center gap-2 text-gray-400">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span>در حال دریافت لیست سفارشات...</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-64 w-full items-center justify-center rounded-xl border border-red-100 bg-red-50 text-red-600">
        خطا در ارتباط با سرور. لطفاً مجدداً تلاش کنید.
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* تولبار بالای جدول */}
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
        <div className="relative w-full max-w-sm">
          <Search className="absolute right-3 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="جستجو در سفارشات..."
            value={globalFilter ?? ""}
            onChange={(event) => setGlobalFilter(event.target.value)}
            className="pr-9 border-gray-200 focus:border-primary focus:ring-primary/20 bg-gray-50/50"
          />
        </div>
        <div className="flex gap-2">
           <Button variant="outline" className="border-dashed border-gray-300 text-gray-600 hover:border-primary hover:text-primary">
              <SlidersHorizontal className="ml-2 h-4 w-4" />
              فیلترها
           </Button>
        </div>
      </div>

      {/* خود جدول */}
      <div className="rounded-xl border border-gray-200 overflow-hidden shadow-sm bg-white">
        <Table>
          {/* هدر اختصاصی برند: پس زمینه تیره، متن طلایی */}
          <TableHeader className="bg-gray-dark">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="hover:bg-gray-dark/90 border-b-gray-700">
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="text-right text-gold-light h-12 font-medium">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  // هاور افکت: رنگ طلایی خیلی ملایم
                  className="hover:bg-gold-light/5 border-b border-gray-100 transition-colors"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-32 text-center text-gray-400">
                  سفارشی با این مشخصات یافت نشد.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* صفحه‌بندی */}
      <div className="flex items-center justify-between px-2">
        <div className="text-xs text-gray-400">
          نمایش {table.getRowModel().rows.length} سفارش
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="text-gray-600 hover:text-primary border-gray-200"
          >
            قبلی
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="text-gray-600 hover:text-primary border-gray-200"
          >
            بعدی
          </Button>
        </div>
      </div>
    </div>
  );
}