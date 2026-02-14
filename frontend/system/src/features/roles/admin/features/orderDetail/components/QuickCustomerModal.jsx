import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { quickCustomerSchema } from "@/features/shared/orders/schemas/orderSchemas";
import { useCreateQuickCustomer } from "../../customers/hooks/useCustomers";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { PlusCircle, Loader2 } from "lucide-react";

const QuickCustomerModal = ({ onCustomerCreated }) => {
  const [open, setOpen] = useState(false);
  
  // هوک اتصال به API
  const { mutate: createCustomer, isPending } = useCreateQuickCustomer((newCustomer) => {
    setOpen(false);
    form.reset();
    // فراخوانی فانکشنی که در کامپوننت والد (OrderCustomerSection) تعریف شده
    // تا مشتری جدید بلافاصله انتخاب شود
    if (onCustomerCreated) {
        onCustomerCreated(newCustomer);
    }
  });

  const form = useForm({
    resolver: zodResolver(quickCustomerSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      phone_number: "",
      company: "",
      // مقادیر پیش‌فرض برای فیلدهای اجباری سیستم که ادمین وقت نکند پر کند
      password: "Password@123", 
      username: "", // اگر خالی باشد، در هوک یا فرم باید با موبایل پر شود
    },
  });

  const onSubmit = (data) => {
    // منطق ساده: اگر نام کاربری وارد نشد، شماره موبایل را نام کاربری کن
    const finalData = {
        ...data,
        username: data.username || data.phone_number,
        email: data.email || `${data.phone_number}@temp.printoo.ir` // ایمیل فیک چون اجباری نیست در ظاهر ولی شاید بکند بخواد
    };
    createCustomer(finalData);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" type="button" className="gap-2">
            <PlusCircle size={16} /> ثبت مشتری جدید
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>ثبت سریع مشتری جدید</DialogTitle>
        </DialogHeader>
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control} name="first_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>نام</FormLabel>
                      <Input {...field} />
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control} name="last_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>نام خانوادگی</FormLabel>
                      <Input {...field} />
                      <FormMessage />
                    </FormItem>
                  )}
                />
            </div>

            <FormField
              control={form.control} name="phone_number"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>شماره موبایل (نام کاربری)</FormLabel>
                  <Input placeholder="0912..." {...field} />
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control} name="company"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>نام شرکت (اختیاری)</FormLabel>
                  <Input {...field} />
                </FormItem>
              )}
            />
            
            {/* فیلد پسورد مخفی یا قابل مشاهده؟ فعلا میذاریم ادمین بدونه دیفالت چیه */}
            <div className="p-3 bg-muted rounded-md text-xs text-muted-foreground">
                * رمز عبور پیش‌فرض: <strong>Password@123</strong> (کاربر می‌تواند بعداً تغییر دهد)
            </div>

            <Button type="submit" className="w-full" disabled={isPending}>
              {isPending ? <Loader2 className="animate-spin" /> : "ثبت مشتری"}
            </Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

export default QuickCustomerModal;