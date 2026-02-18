import React, { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"; // نیاز به نصب: npm i @radix-ui/react-dialog
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Save } from "lucide-react";
import CitySelector from "./CitySelector";

const AddressDialog = ({ open, onOpenChange, onSubmit, initialData, isSubmitting }) => {
  const [formData, setFormData] = useState({
    province_id: "",
    city_id: "",
    postal_code: "",
    address: "",
  });

  // وقتی دیالوگ باز میشه یا دیتای اولیه تغییر میکنه (برای ادیت)
  useEffect(() => {
    if (open) {
      if (initialData) {
        // نکته: چون API در GET آدرس، اسم شهر رو میده ولی در PUT آیدی میخواد،
        // در حالت ادیت، کاربر مجبوره استان/شهر رو دوباره انتخاب کنه مگر اینکه بک‌ند ID رو بفرسته.
        // اینجا ما سایر فیلدها رو پر میکنیم.
        setFormData({
            province_id: initialData.province_id || "", // اگر بک‌ند فرستاد
            city_id: initialData.city_id || "",         // اگر بک‌ند فرستاد
            postal_code: initialData.postal_code || "",
            address: initialData.address || "",
        });
      } else {
        // حالت افزودن: فرم خالی
        setFormData({ province_id: "", city_id: "", postal_code: "", address: "" });
      }
    }
  }, [open, initialData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{initialData ? "ویرایش آدرس" : "افزودن آدرس جدید"}</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
           {/* انتخاب شهر و استان */}
           <CitySelector 
              onProvinceChange={(id) => setFormData(prev => ({ ...prev, province_id: id }))}
              onCityChange={(id) => setFormData(prev => ({ ...prev, city_id: id }))}
           />
           
           {/* نمایش پیام در حالت ادیت اگر آیدی شهر نداریم */}
           {initialData && !initialData.city_id && (
               <div className="text-xs text-amber-600 bg-amber-50 p-2 rounded">
                   توجه: لطفاً استان و شهر را مجدداً انتخاب کنید.
               </div>
           )}

           <div className="space-y-2">
              <Label>کد پستی</Label>
              <Input 
                value={formData.postal_code} 
                onChange={(e) => setFormData({...formData, postal_code: e.target.value})} 
                className="font-mono dir-ltr" 
              />
           </div>

           <div className="space-y-2">
              <Label>متن آدرس</Label>
              <Textarea 
                value={formData.address} 
                onChange={(e) => setFormData({...formData, address: e.target.value})} 
                placeholder="خیابان، کوچه، پلاک..."
              />
           </div>

           <div className="flex justify-end pt-2">
              <Button type="submit" className="bg-gold-dark hover:bg-gold-dark/90 text-slate-900 font-bold" disabled={isSubmitting}>
                 {isSubmitting ? <Loader2 className="animate-spin ml-2 h-4 w-4"/> : <Save className="ml-2 h-4 w-4"/>}
                 ذخیره آدرس
              </Button>
           </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddressDialog;