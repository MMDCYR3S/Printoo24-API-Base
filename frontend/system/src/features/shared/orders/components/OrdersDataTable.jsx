import React, { useState } from "react";
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
import { getColumns } from "./columns"; // ستون‌های حرفه‌ای که نوشتیم
import { useOrderActions } from "../hooks/useOrders"; // هوک عملیات سریع
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, FilterX } from "lucide-react";

const OrdersDataTable = ({ data = [], isLoading }) => {
  const [sorting, setSorting] = useState([]);
  const [columnFilters, setColumnFilters] = useState([]);
  const { approve, reject } = useOrderActions();

  // هندلرهای عملیات سریع
  const handleApprove = (id) => {
    if (window.confirm("آیا از تایید و ارسال به مرحله بعد اطمینان دارید؟")) {
      approve.mutate(id);
    }
  };

  const handleReject = (id) => {
    const reason = window.prompt("علت رد سفارش را بنویسید:");
    if (reason !== null) {
      reject.mutate({ id, description: reason });
    }
  };

  // دریافت ستون‌ها و تزریق توابع عملیاتی
  const columns = getColumns(handleApprove, handleReject);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
    },
  });

  if (isLoading) return <div className="p-8 text-center">در حال بارگذاری سفارشات...</div>;

  return (
    <div className="space-y-4">
      {/* 🔍 بخش فیلترها */}
      <div className="flex flex-col md:flex-row items-end gap-4 bg-white p-4 rounded-lg border shadow-sm">
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <label className="text-xs font-bold text-gray-500 mr-1">جستجوی مشتری / کد</label>
          <div className="relative">
            <Search className="absolute right-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="نام مشتری یا کد سفارش..."
              value={(table.getColumn("recipient_name")?.getFilterValue() || "")}
              onChange={(event) =>
                table.getColumn("recipient_name")?.setFilterValue(event.target.value)
              }
              className="pr-9"
            />
          </div>
        </div>

        <div className="grid w-full max-w-[200px] items-center gap-1.5">
          <label className="text-xs font-bold text-gray-500 mr-1">فیلتر وضعیت</label>
          <Select
            value={(table.getColumn("status_display")?.getFilterValue() || "all")}
            onValueChange={(value) => 
                table.getColumn("status_display")?.setFilterValue(value === "all" ? "" : value)
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="همه وضعیت‌ها" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">همه وضعیت‌ها</SelectItem>
              <SelectItem value="تایید">تایید شده</SelectItem>
              <SelectItem value="طراحی">در حال طراحی</SelectItem>
              <SelectItem value="چاپ">در حال چاپ</SelectItem>
              <SelectItem value="ارسال">آماده ارسال</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => table.resetColumnFilters()}
          className="text-xs text-gray-400"
        >
          <FilterX className="ml-2 h-4 w-4" /> حذف فیلترها
        </Button>
      </div>

      {/* 📊 جدول اصلی */}
      <div className="rounded-md border bg-white shadow-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="text-xs font-bold text-gray-600">
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  className="hover:bg-blue-50/30 transition-colors"
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
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  سفارشی یافت نشد.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* 📄 پجینیشن */}
      <div className="flex items-center justify-between px-2">
        <div className="text-xs text-muted-foreground">
            نمایش {table.getRowModel().rows.length} از {data.length} سفارش
        </div>
        <div className="flex items-center space-x-2 space-x-reverse">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            قبلی
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            بعدی
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OrdersDataTable;