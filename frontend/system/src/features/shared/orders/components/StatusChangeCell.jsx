import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ORDER_STATUSES } from "../utils/orderStatusConfig";
import { Check, ChevronsUpDown, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useOrderActions } from "../hooks/useOrders";

// تابع کمکی برای پیدا کردن کانفیگ
const findStatusConfig = (statusValue) => {
  // 🛑 فیکس حیاتی: به جای برگرداندن null، یک آبجکت پیش‌فرض امن برمی‌گردانیم
  if (!statusValue) {
    return {
      label: "بدون وضعیت",
      icon: ChevronsUpDown,
      color: "bg-gray-100 text-gray-500 border-gray-200"
    };
  }
  
  let config = ORDER_STATUSES.find(s => s.value === statusValue);
  if (!config) {
    config = ORDER_STATUSES.find(s => s.label === statusValue);
  }
  
  return config || {
    label: statusValue,
    icon: ChevronsUpDown,
    color: "bg-gray-100 text-gray-600 border-gray-200"
  };
};

const StatusChangeCell = ({ orderId, currentStatus }) => {
  const [open, setOpen] = useState(false);
  const { changeStatus, isChanging } = useOrderActions(); 
  
  const config = findStatusConfig(currentStatus);
  // 🛑 فیکس محافظتی دوم: استفاده از علامت ؟ برای جلوگیری از کرش
  const StatusIcon = config?.icon || ChevronsUpDown;

  const handleSelect = (newStatusCode) => {
    // بستن سریع منو
    setOpen(false);
    
    // اگر همان وضعیت قبلی بود کاری نکن
    if (newStatusCode === currentStatus) return;

    changeStatus.mutate({ 
        id: orderId, 
        statusCode: newStatusCode, 
        description: "تغییر دستی توسط ادمین" 
    });
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline" // استفاده از outline برای حس صنعتی
          role="combobox"
          aria-expanded={open}
          onClick={(e) => e.stopPropagation()} 
          className={cn(
            "h-8 text-[11px] font-bold border rounded-md px-2.5 transition-all shadow-sm w-full justify-between",
            // استایل صنعتی: رنگ پس‌زمینه سالید خیلی کمرنگ + بوردر مشخص
            config?.color 
          )}
        >
          {isChanging ? (
             <Loader2 className="mr-1.5 h-3 w-3 animate-spin" />
          ) : (
            <div className="flex items-center gap-2 truncate">
                {/* نمایش آیکون */}
                <StatusIcon className="h-3.5 w-3.5 opacity-70" />
                <span>{config?.label}</span>
            </div>
          )}
          <ChevronsUpDown className="ml-1 h-3 w-3 shrink-0 opacity-30" />
        </Button>
      </PopoverTrigger>

      {/* 🛑 جلوگیری از بسته شدن هنگام کلیک داخل منو */}
      <PopoverContent 
        className="w-[200px] p-0 shadow-xl border-gold-dark/20 z-50" 
        align="start"
        onClick={(e) => e.stopPropagation()}
      >
        <Command>
          <CommandInput placeholder="جستجو..." className="h-9 text-xs text-right" />
          <CommandList>
            <CommandEmpty className="py-2 text-xs text-center text-gray-500">یافت نشد.</CommandEmpty>
            <CommandGroup heading="انتخاب وضعیت جدید">
                {ORDER_STATUSES.map((status) => (
                <CommandItem
                    key={status.value}
                    value={status.label} // 🛑 ولیو را لیبل فارسی میگذاریم که با سرچ همخوانی داشته باشد
                    onSelect={() => handleSelect(status.value)}
                    // 🛑 کلاس pointer-events-auto یعنی به زور کلیک را قبول کن!
                    className={cn(
                        "text-xs cursor-pointer gap-2 py-2 pointer-events-auto data-[disabled]:pointer-events-auto data-[disabled]:opacity-100", 
                        currentStatus === status.value ? "bg-gold-dark/10" : ""
                    )}
                >
                    <div className={cn(
                        "flex h-4 w-4 items-center justify-center rounded-full border border-gray-300",
                        (currentStatus === status.label || currentStatus === status.value) 
                            ? "bg-gold-dark border-gold-dark text-white" 
                            : ""
                    )}>
                        {(currentStatus === status.label || currentStatus === status.value) && <Check className="h-3 w-3" />}
                    </div>
                    {/* رندر امن آیکون در لیست */}
                    {status.icon && <status.icon className="h-4 w-4 text-muted-foreground" />}
                    <span className="font-medium">{status.label}</span>
                </CommandItem>
                ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

export default StatusChangeCell;