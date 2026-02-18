import React, { useState, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { staffService } from "../api/staffService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch"; 
import { toast } from "sonner";
import { Loader2, Save, UserPlus, UserCog } from "lucide-react";

const StaffForm = ({ staffToEdit, onSuccess }) => {
  const queryClient = useQueryClient();
  const isEditMode = !!staffToEdit;

  // دریافت لیست نقش‌ها
  const { data: roles = [] } = useQuery({
    queryKey: ["roles"],
    queryFn: staffService.getAllRoles,
  });

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role_id: "",
    is_active: true,
  });

  useEffect(() => {
    if (staffToEdit) {
      setFormData({
        username: staffToEdit.username,
        email: staffToEdit.email,
        password: "", // در ویرایش پسورد نداریم
        role_id: staffToEdit.role_id,
        is_active: staffToEdit.is_active,
      });
    }
  }, [staffToEdit]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditMode) {
        // طبق داکیومنت: PUT فقط role_id و is_active میگیره
        return staffService.updateStaff({ 
            id: staffToEdit.id, 
            data: { role_id: Number(data.role_id), is_active: data.is_active } 
        });
      } else {
        return staffService.createStaff({
            ...data,
            role_id: Number(data.role_id)
        });
      }
    },
    onSuccess: () => {
      toast.success(isEditMode ? "اطلاعات کارمند بروز شد" : "کارمند جدید استخدام شد");
      queryClient.invalidateQueries({ queryKey: ["staff"] });
      onSuccess();
    },
    onError: (err) => {
      const msg = err.response?.data?.detail || "خطا در انجام عملیات";
      toast.error(msg);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 mt-4">
      
      {/* فقط در حالت ایجاد نمایش داده شود */}
      {!isEditMode && (
          <div className="space-y-4 border p-4 rounded-md bg-slate-50/50">
             <div className="flex items-center gap-2 text-slate-700 font-bold border-b pb-2 mb-2">
                <UserPlus className="h-4 w-4" /> اطلاعات احراز هویت
             </div>
             <div className="space-y-2">
                <Label>نام کاربری (انگلیسی) <span className="text-red-500">*</span></Label>
                <Input name="username" value={formData.username} onChange={handleChange} required className="dir-ltr font-mono" />
             </div>
             <div className="space-y-2">
                <Label>ایمیل (سازمانی) <span className="text-red-500">*</span></Label>
                <Input name="email" type="email" value={formData.email} onChange={handleChange} required className="dir-ltr font-mono" />
             </div>
             <div className="space-y-2">
                <Label>رمز عبور <span className="text-red-500">*</span></Label>
                <Input name="password" type="password" value={formData.password} onChange={handleChange} required className="dir-ltr font-mono" placeholder="حداقل ۸ کاراکتر" />
             </div>
          </div>
      )}

      {/* در حالت ویرایش فقط نام کاربری را نمایش میدهیم (غیرقابل تغییر) */}
      {isEditMode && (
         <div className="p-4 bg-slate-100 rounded text-center">
            <span className="text-xs text-slate-500 block">در حال ویرایش دسترسی:</span>
            <span className="font-bold text-lg text-slate-800">{formData.username}</span>
         </div>
      )}

      <div className="space-y-4 border p-4 rounded-md bg-white">
         <div className="flex items-center gap-2 text-slate-700 font-bold border-b pb-2 mb-2">
            <UserCog className="h-4 w-4" /> تنظیمات دسترسی
         </div>
         
         <div className="space-y-2">
            <Label>نقش سازمانی <span className="text-red-500">*</span></Label>
            <select 
                name="role_id" 
                value={formData.role_id} 
                onChange={handleChange}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                required
            >
                <option value="">انتخاب نقش...</option>
                {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name || role.label}</option>
                ))}
            </select>
         </div>

         <div className="flex items-center justify-between border p-3 rounded-md bg-slate-50 mt-4">
             <div className="space-y-0.5">
                <Label className="text-base">وضعیت حساب</Label>
                <p className="text-xs text-slate-500">آیا این کارمند اجازه ورود دارد؟</p>
             </div>
             <Switch 
                checked={formData.is_active} 
                onCheckedChange={(checked) => setFormData(prev => ({...prev, is_active: checked}))}
             />
         </div>
      </div>

      <div className="pt-4 sticky bottom-0 bg-white border-t">
        <Button type="submit" className="w-full bg-slate-900 hover:bg-slate-800 font-bold" disabled={mutation.isPending}>
            {mutation.isPending ? <Loader2 className="animate-spin h-4 w-4" /> : <Save className="h-4 w-4 mr-2" />}
            {isEditMode ? "ذخیره تغییرات" : "استخدام کارمند"}
        </Button>
      </div>
    </form>
  );
};

export default StaffForm;