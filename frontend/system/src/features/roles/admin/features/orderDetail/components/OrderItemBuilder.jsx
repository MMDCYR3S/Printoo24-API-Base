import React from "react";
import { useFieldArray, useFormContext } from "react-hook-form";
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Trash2, Plus, Package } from "lucide-react";
import { Separator } from "@/components/ui/separator";

const OrderItemBuilder = () => {
  const { control } = useFormContext();
  
  // مدیریت آرایه اقلام (Add/Remove داینامیک)
  const { fields, append, remove } = useFieldArray({
    control,
    name: "items",
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Package className="w-5 h-5 text-primary" />
          اقلام سفارش
        </h3>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append({ product_name: "", quantity: 1, width: "", height: "", description: "" })}
          className="gap-2"
        >
          <Plus size={16} />
          افزودن محصول
        </Button>
      </div>

      {fields.map((field, index) => (
        <Card key={field.id} className="relative border-dashed border-2 hover:border-solid transition-colors">
          <CardContent className="pt-6 grid gap-4">
            
            {/* دکمه حذف (فقط اگر بیشتر از ۱ آیتم باشد) */}
            {fields.length > 1 && (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute left-2 top-2 text-destructive hover:bg-destructive/10"
                onClick={() => remove(index)}
              >
                <Trash2 size={18} />
              </Button>
            )}

            {/* ردیف اول: نام محصول و تعداد */}
            <div className="grid grid-cols-12 gap-4">
              <div className="col-span-8 md:col-span-9">
                <FormField
                  control={control}
                  name={`items.${index}.product_name`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>عنوان محصول / خدمت <span className="text-red-500">*</span></FormLabel>
                      <FormControl>
                        <Input placeholder="مثال: بنر فلکس عرض ۳ متر" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="col-span-4 md:col-span-3">
                <FormField
                  control={control}
                  name={`items.${index}.quantity`}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>تعداد</FormLabel>
                      <FormControl>
                        <Input type="number" min={1} {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <Separator />

            {/* ردیف دوم: ابعاد و توضیحات (Optional) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <FormField
                control={control}
                name={`items.${index}.width`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>طول (cm)</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="اختیاری" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={control}
                name={`items.${index}.height`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>عرض (cm)</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="اختیاری" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
              <FormField
                control={control}
                name={`items.${index}.description`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>توضیحات فنی آیتم</FormLabel>
                    <FormControl>
                      <Input placeholder="مثال: دوربری شود، پانچ شود..." {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />
            </div>
          </CardContent>
        </Card>
      ))}
      
      {fields.length === 0 && (
        <div className="text-center p-8 border-2 border-dashed rounded-lg text-muted-foreground bg-muted/20">
            هیچ محصولی اضافه نشده است.
        </div>
      )}
    </div>
  );
};

export default OrderItemBuilder;