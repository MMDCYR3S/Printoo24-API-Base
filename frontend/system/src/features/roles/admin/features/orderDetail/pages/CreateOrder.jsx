import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function CreateOrder() {
  return (
    <div className="max-w-2xl mx-auto space-y-8 p-6 bg-white rounded-lg shadow-sm border">
      <div>
        <h3 className="text-lg font-medium">ایجاد سفارش جدید</h3>
        <p className="text-sm text-gray-500">اطلاعات اولیه سفارش را وارد کنید.</p>
      </div>
      <div className="grid gap-4">
        <div className="grid gap-2">
          <Label htmlFor="title">عنوان سفارش</Label>
          <Input id="title" placeholder="مثلاً: کارت ویزیت شرکت X" />
        </div>
        <Button>ثبت اولیه سفارش</Button>
      </div>
    </div>
  );
}