import React, { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "../api/customerService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea"; // نیاز به نصب یا فایل دارد، اگر ندارید Input معمولی بگذارید
import { Switch } from "@/components/ui/switch"; // نیاز به نصب: npm install @radix-ui/react-switch
import { toast } from "sonner";
import { Loader2, Save } from "lucide-react";

const CustomerForm = ({ customerToEdit, onSuccess }) => {
  const queryClient = useQueryClient();
  const isEditMode = !!customerToEdit;

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    company: "",
    is_active: true,
    bio: "",
  });

  // پر کردن فرم در حالت ویرایش
  useEffect(() => {
    if (customerToEdit) {
      setFormData({
        ...customerToEdit,
        password: "", // رمز عبور در ویرایش خالی باشد مگر اینکه بخواهد تغییر دهد
      });
    }
  }, [customerToEdit]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditMode) {
        // حذف پسورد اگر خالی باشد تا هش نشود
        const updatePayload = { ...data };
        if (!updatePayload.password) delete updatePayload.password;
        return customerService.updateCustomer({ id: customerToEdit.id, data: updatePayload });
      } else {
        // return customerService.createCustomer(data);
        return customerService.createQuickCustomer(data);
      }
    },
    onSuccess: () => {
      toast.success(isEditMode ? "مشتری با موفقیت ویرایش شد" : "مشتری جدید ایجاد شد");
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      onSuccess(); // بستن شیت
    },
    onError: (err) => {
      const msg = err.response?.data?.message || "خطا در ذخیره اطلاعات";
      toast.error(msg);
    },
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-4">
      
      {/* اطلاعات کاربری */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
            <Label htmlFor="first_name">نام</Label>
            <Input id="first_name" name="first_name" value={formData.first_name} onChange={handleChange} required />
        </div>
        <div className="space-y-2">
            <Label htmlFor="last_name">نام خانوادگی</Label>
            <Input id="last_name" name="last_name" value={formData.last_name} onChange={handleChange} required />
        </div>
      </div>

      <div className="space-y-2">
         <Label htmlFor="username">نام کاربری (انگلیسی)</Label>
         <Input id="username" name="username" value={formData.username} onChange={handleChange} required disabled={isEditMode} className="font-mono" />
      </div>

      {!isEditMode && (
          <div className="space-y-2">
            <Label htmlFor="password">رمز عبور</Label>
            <Input id="password" name="password" type="password" value={formData.password} onChange={handleChange} required className="font-mono" />
          </div>
      )}

      {/* اطلاعات تماس */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
            <Label htmlFor="phone_number">شماره موبایل</Label>
            <Input id="phone_number" name="phone_number" value={formData.phone_number} onChange={handleChange} required className="font-mono dir-ltr" />
        </div>
        <div className="space-y-2">
            <Label htmlFor="email">ایمیل (اختیاری)</Label>
            <Input id="email" name="email" type="email" value={formData.email} onChange={handleChange} className="font-mono" />
        </div>
      </div>

      <div className="space-y-2">
         <Label htmlFor="company">نام شرکت / سازمان</Label>
         <Input id="company" name="company" value={formData.company} onChange={handleChange} />
      </div>

      {isEditMode && (
         <div className="flex items-center gap-2 border p-3 rounded-md bg-slate-50">
             <input 
                type="checkbox" 
                id="is_active" 
                checked={formData.is_active} 
                onChange={(e) => setFormData(prev => ({...prev, is_active: e.target.checked}))}
                className="w-4 h-4 text-gold-dark rounded border-gray-300 focus:ring-gold-dark"
             />
             <Label htmlFor="is_active" className="cursor-pointer">حساب کاربری فعال است</Label>
         </div>
      )}

      <div className="pt-4 sticky bottom-0 bg-white pb-4 border-t mt-6">
        <Button type="submit" className="w-full bg-gold-dark hover:bg-gold-dark/90 text-slate-900 font-bold gap-2" disabled={mutation.isPending}>
            {mutation.isPending ? <Loader2 className="animate-spin h-4 w-4" /> : <Save className="h-4 w-4" />}
            {isEditMode ? "ذخیره تغییرات" : "ثبت مشتری جدید"}
        </Button>
      </div>
    </form>
  );
};

export default CustomerForm;