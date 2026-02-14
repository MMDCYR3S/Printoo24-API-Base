import React, { useEffect } from "react";
import { useForm, useFieldArray, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { createOrderSchema } from "@/features/shared/orders/schemas/orderSchemas";
import { useCreateOrder } from "@/features/shared/orders/hooks/useOrders";
import { useNavigate } from "react-router-dom";

// Components
import OrderCustomerSection from "../components/OrderCustomerSection"; // اضافه شد
import ItemSelectionsDialog from "../components/ItemSelectionsDialog"; // اضافه شد
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
// پیدا کن و جایگزین کن:
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, Plus, Save, ArrowRight } from "lucide-react";

import { useOrderStatusList } from "@/features/shared/orders/hooks/useOrders";
import FileUploader from "@/features/shared/orders/components/FileUploader";


const CreateOrder = () => {
  const { data: statuses } = useOrderStatusList();
  const navigate = useNavigate();
  const { mutate: createOrder, isPending } = useCreateOrder();

  const form = useForm({
    resolver: zodResolver(createOrderSchema),
    defaultValues: {
      user_id: "", // حالا دیگه user_id داریم
      recipient_name: "",
      recipient_phone: "",
      full_address: "",
      price: 0,
      items: [
        { name: "", description: "", item_price: 0, quantity: 1, selections: {} }
      ],
    },
  });

  const { control, handleSubmit, setValue } = form;
  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  // محاسبه قیمت
  const itemsParams = useWatch({ control, name: "items" });
  useEffect(() => {
    const calculatedTotal = itemsParams.reduce((sum, item) => {
      return sum + (Number(item.item_price || 0) * Number(item.quantity || 1));
    }, 0);
    if (calculatedTotal > 0) setValue("price", calculatedTotal);
  }, [itemsParams, setValue]);

  const onSubmit = (data) => createOrder(data);

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowRight className="w-4 h-4" />
        </Button>
        <h1 className="text-2xl font-bold">ثبت سفارش اختصاصی</h1>
      </div>

      <Form {...form}>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          
          {/* ۱. بخش انتخاب مشتری (اصلاح شده) */}
          <OrderCustomerSection />

          {/* ۲. جدول اقلام سفارش */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base font-medium">اقلام سفارش</CardTitle>
              <Button 
                type="button" size="sm" variant="secondary"
                onClick={() => append({ name: "", description: "", item_price: 0, quantity: 1, selections: {} })}
              >
                <Plus className="w-4 h-4 ml-2" /> افزودن سطر
              </Button>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[20%]">محصول</TableHead>
                    <TableHead className="w-[25%]">توضیحات</TableHead>
                    <TableHead className="w-[15%]">ویژگی‌ها (Selections)</TableHead>
                    <TableHead className="w-[15%]">فی</TableHead>
                    <TableHead className="w-[10%]">تعداد</TableHead>
                    <TableHead className="w-[10%]">جمع</TableHead>
                    <TableHead className="w-[5%]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {fields.map((field, index) => (
                    <TableRow key={field.id}>
                      <TableCell>
                        <FormField control={control} name={`items.${index}.name`}
                          render={({ field }) => (
                            <FormItem><FormControl><Input placeholder="نام محصول" {...field} /></FormControl><FormMessage /></FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        <FormField control={control} name={`items.${index}.description`}
                          render={({ field }) => (
                            <FormItem><FormControl><Input placeholder="توضیحات..." {...field} /></FormControl></FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        {/* دکمه مدیریت ویژگی‌ها (Selections) */}
                        <FormField control={control} name={`items.${index}.selections`}
                          render={({ field }) => (
                            <ItemSelectionsDialog value={field.value} onChange={field.onChange} />
                          )}
                        />
                      </TableCell>
                      <TableCell>
                         <FormField control={control} name={`items.${index}.item_price`}
                          render={({ field }) => (
                            <FormItem><FormControl><Input type="number" {...field} /></FormControl></FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell>
                        <FormField control={control} name={`items.${index}.quantity`}
                          render={({ field }) => (
                            <FormItem><FormControl><Input type="number" min={1} className="text-center" {...field} /></FormControl></FormItem>
                          )}
                        />
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm font-mono">
                         {( (form.getValues(`items.${index}.item_price`) || 0) * (form.getValues(`items.${index}.quantity`) || 0) ).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {fields.length > 1 && (
                            <Button variant="ghost" size="icon" className="text-red-500" onClick={() => remove(index)}>
                                <Trash2 className="w-4 h-4" />
                            </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* ۳. فوتر مالی */}
          <div className="flex justify-end">
             <Card className="w-full md:w-1/3 bg-muted/20">
                  

                  
                <CardContent className="pt-6 space-y-4">



                    <FormField control={control} name="price"
                        render={({ field }) => (
                            <div className="flex justify-between items-center">
                                <span className="font-bold">مبلغ نهایی:</span>
                                <Input className="w-1/2 font-bold bg-background" type="number" {...field} />
                            </div>
                        )}
                    />

<div className="space-y-4 border-t pt-4">
    <FormField
        control={control}
        name="initial_status"
        render={({ field }) => (
            <FormItem>
                <FormLabel>تعیین وضعیت اولیه</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                        <SelectTrigger>
                            <SelectValue placeholder="انتخاب وضعیت..." />
                        </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                        {statuses?.map((s) => (
                            <SelectItem key={s.internal_code} value={s.internal_code}>
                                {s.name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </FormItem>
        )}
    />

    <div className="space-y-2">
        <label className="text-sm font-medium">پیوست‌های کلی سفارش</label>
        <FormField
            control={control}
            name="attachments"
            render={({ field }) => (
                <FileUploader value={field.value} onChange={field.onChange} />
            )}
        />
    </div>
</div>


                    <Button type="submit" className="w-full" disabled={isPending}>
                        {isPending ? "در حال ثبت..." : "ثبت سفارش"} <Save className="mr-2 w-4 h-4" />
                    </Button>
                </CardContent>
             </Card>
             
          </div>
        </form>
      </Form>
    </div>
  );
};

export default CreateOrder;