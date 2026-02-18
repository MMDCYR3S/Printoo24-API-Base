import React, { useState } from "react";
import {
  flexRender, getCoreRowModel, useReactTable,
  getPaginationRowModel, getFilteredRowModel, getSortedRowModel, getFacetedUniqueValues
} from "@tanstack/react-table";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { columns } from "./columns";
import OrdersToolbar from "./OrdersToolbar";
import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

const OrdersDataTable = ({ data = [], columns: customColumns, isLoading, onDeleteBulk }) => {
  const [rowSelection, setRowSelection] = useState({});
  const [columnFilters, setColumnFilters] = useState([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const tableColumns = customColumns || columns;

  const table = useReactTable({
    data,
    columns: tableColumns,
    state: { rowSelection, columnFilters, globalFilter },
    onRowSelectionChange: setRowSelection,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
  });

  const selectedRows = table.getSelectedRowModel().rows.map(r => r.original.id);

  // 📐 مهندسی دقیق سایز ستون‌ها (با قابلیت Override از سمت Column Definition)
  const getColumnStyles = (columnId, columnDef) => {
    // ⭐️ اگر در تعریف ستون، کلاس خاصی برای عرض داده بودیم، از همان استفاده کن
    if (columnDef?.meta?.className) return columnDef.meta.className;

    switch (columnId) {
      case "select":
        return "w-[50px] min-w-[50px] max-w-[50px] justify-center";
      case "order_code":
        return "w-[130px] min-w-[130px] justify-center font-mono";
      case "recipient_name":
        return "flex-1 min-w-[250px] justify-start text-right"; 
      case "total_price":
        return "w-[140px] min-w-[140px] justify-end text-left pl-4";
      case "created_at":
        return "w-[140px] min-w-[140px] justify-end text-left";
      case "internal_code":
      case "status_display": 
        return "w-[180px] min-w-[180px] justify-center";
      case "actions":
        return "w-[60px] min-w-[60px] justify-center";
      default:
        return "w-auto justify-start";
    }
  };

  return (
    <div className="space-y-5 p-2">
      <div className="flex flex-col gap-4">
        {selectedRows.length > 0 && (
            <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-2 rounded-lg flex justify-between items-center animate-in slide-in-from-top-2">
                <span className="text-sm font-bold">{selectedRows.length} سفارش انتخاب شده</span>
                <Button variant="destructive" size="sm" onClick={() => onDeleteBulk(selectedRows)} className="gap-2 shadow-sm">
                    <Trash2 size={14} /> حذف موارد انتخاب شده
                </Button>
            </div>
        )}
        
        <div className="bg-white p-1 rounded-t-xl border-b border-dashed">
             <OrdersToolbar table={table} />
        </div>

        <div className="rounded-xl overflow-visible">
             <Table>
                <TableHeader className="bg-transparent border-b-0 mb-3 block px-1">
                    {table.getHeaderGroups().map(hg => (
                    <TableRow key={hg.id} className="hover:bg-transparent border-0 flex items-center gap-4 px-4 w-full">
                        {hg.headers.map(header => (
                        <TableHead 
                            key={header.id} 
                            className={cn(
                                "text-xs font-bold text-slate-400 h-auto py-2 flex items-center",
                                getColumnStyles(header.column.id, header.column.columnDef) // پاس دادن ColumnDef برای چک کردن Meta
                            )}
                        >
                            {flexRender(header.column.columnDef.header, header.getContext())}
                        </TableHead>
                        ))}
                    </TableRow>
                    ))}
                </TableHeader>
                
                <TableBody className="space-y-2 block ">
                    {isLoading ? (
                        <div className="text-center py-20 text-slate-400 bg-white rounded-xl border border-dashed border-slate-200">
                            <span className="loading loading-dots loading-md"></span> در حال بارگذاری...
                        </div>
                    ) : table.getRowModel().rows.length ? (
                    table.getRowModel().rows.map(row => (
                        <TableRow 
                            key={row.id} 
                            className="bg-white rounded-lg hover:bg-slate-100 shadow-[0_2px_12px_-4px_rgba(0,0,0,0.08)] transition-all flex items-center gap-4 px-4 py-3 w-full group relative overflow-hidden"
                        >
                            {row.getVisibleCells().map(cell => (
                                <TableCell 
                                    key={cell.id} 
                                    className={cn(
                                        "py-0 border-0 flex items-center p-0", 
                                        getColumnStyles(cell.column.id, cell.column.columnDef)
                                    )}
                                >
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))
                    ) : (
                    <div className="bg-white rounded-xl border border-dashed border-slate-300 p-16 text-center text-slate-500 flex flex-col items-center justify-center gap-2">
                        <span className="text-4xl">📭</span>
                        <span className="font-medium">هیچ سفارشی یافت نشد</span>
                    </div>
                    )}
                </TableBody>
            </Table>
        </div>
      </div>

      <div className="flex items-center justify-between px-4 pt-2 border-t border-slate-100 mt-4">
         <div className="text-xs text-slate-400 font-medium">
            صفحه {table.getState().pagination.pageIndex + 1} از {table.getPageCount()}
         </div>
         <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} className="h-8 text-xs">قبلی</Button>
            <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} className="h-8 text-xs">بعدی</Button>
         </div>
      </div>
    </div>
  );
};

export default OrdersDataTable;