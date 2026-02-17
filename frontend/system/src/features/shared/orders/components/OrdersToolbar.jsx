import React from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X, Filter, Check } from "lucide-react";
import { ORDER_STATUSES } from "../utils/orderStatusConfig";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Command, CommandGroup, CommandItem, CommandList, CommandSeparator, CommandEmpty, CommandInput } from "@/components/ui/command";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

const OrdersToolbar = ({ table }) => {
  const isFiltered = table.getState().columnFilters.length > 0;

  return (
    <div className="flex items-center justify-between p-4 bg-white">
      <div className="flex flex-1 items-center space-x-2 space-x-reverse">
        {/* سرچ سراسری */}
        <div className="relative">
             <Input
                placeholder="جستجو (نام، موبایل، کد)..."
                value={(table.getState().globalFilter) ?? ""}
                onChange={(event) => table.setGlobalFilter(event.target.value)}
                className="h-9 w-[200px] lg:w-[300px] bg-slate-50 border-slate-200 focus:border-gold-dark rounded-md text-xs"
            />
        </div>

        {/* فیلتر مولتی سلکت وضعیت */}
        <StatusMultiSelectFilter table={table} />

        {isFiltered && (
          <Button
            variant="ghost"
            onClick={() => table.resetColumnFilters()}
            className="h-8 px-2 lg:px-3 text-red-500 hover:text-red-600 hover:bg-red-50 text-xs rounded-md"
          >
            پاک کردن فیلترها
            <X className="mr-2 h-3.5 w-3.5" />
          </Button>
        )}
      </div>
    </div>
  );
};

// 🛠️ کامپوننت فیلتر چندگانه (Multi-Select)
const StatusMultiSelectFilter = ({ table }) => {
    const column = table.getColumn("internal_code"); // مطمئن شو نام ستون در columns.jsx همین باشد
    const selectedValues = new Set(column?.getFilterValue() || []);
  
    return (
      <Popover>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="h-9 border-dashed border-slate-300 rounded-md text-xs">
            <Filter className="ml-2 h-3.5 w-3.5 text-slate-500" />
            فیلتر وضعیت
            {selectedValues?.size > 0 && (
              <>
                <Separator orientation="vertical" className="mx-2 h-4" />
                <Badge variant="secondary" className="rounded-sm px-1 font-normal lg:hidden bg-slate-100 text-slate-700">
                  {selectedValues.size}
                </Badge>
                <div className="hidden space-x-1 space-x-reverse lg:flex">
                  {selectedValues.size > 2 ? (
                    <Badge variant="secondary" className="rounded-sm px-1 font-normal bg-slate-100 text-slate-700">
                      {selectedValues.size} انتخاب شده
                    </Badge>
                  ) : (
                    ORDER_STATUSES
                        .filter((option) => selectedValues.has(option.value))
                        .map((option) => (
                            <Badge variant="secondary" key={option.value} className="rounded-sm px-1 font-normal bg-slate-100 text-slate-700 gap-1">
                                {option.label}
                            </Badge>
                    ))
                  )}
                </div>
              </>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[240px] p-0 rounded-md" align="start">
          <Command>
            <CommandInput placeholder="جستجوی وضعیت..." className="h-9 text-xs" />
            <CommandList>
              <CommandEmpty>یافت نشد.</CommandEmpty>
              <CommandGroup>
                {ORDER_STATUSES.map((option) => {
                  const isSelected = selectedValues.has(option.value);
                  return (
                    <CommandItem
                      key={option.value}
                      onSelect={() => {
                        // منطق مولتی سلکت: اگر بود حذف کن، نبود اضافه کن
                        const newSelectedValues = new Set(selectedValues);
                        if (isSelected) {
                            newSelectedValues.delete(option.value);
                        } else {
                            newSelectedValues.add(option.value);
                        }
                        const filterValues = Array.from(newSelectedValues);
                        column?.setFilterValue(filterValues.length ? filterValues : undefined);
                      }}
                      className="cursor-pointer text-xs"
                    >
                      <div className={cn(
                          "ml-2 flex h-4 w-4 items-center justify-center rounded-sm border border-slate-300",
                          isSelected ? "bg-gold-dark border-gold-dark text-white" : "opacity-50 [&_svg]:invisible"
                      )}>
                        <Check className="h-3 w-3" />
                      </div>
                      <option.icon className="ml-2 h-3.5 w-3.5 text-slate-500" />
                      <span>{option.label}</span>
                    </CommandItem>
                  );
                })}
              </CommandGroup>
              {selectedValues.size > 0 && (
                <>
                  <CommandSeparator />
                  <CommandGroup>
                    <CommandItem
                      onSelect={() => column?.setFilterValue(undefined)}
                      className="justify-center text-center text-xs font-bold text-red-500 cursor-pointer"
                    >
                      پاک کردن همه
                    </CommandItem>
                  </CommandGroup>
                </>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    );
};

export default OrdersToolbar;