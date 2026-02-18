import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "../api/customerService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch"; 
import { toast } from "sonner";
import { Loader2, Save, MapPin, User, ArrowRight, Building2, AlertTriangle } from "lucide-react";
import CitySelector from "../components/CitySelector"; // کامپوننت جدید

const CreateCustomer = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [hasAddress, setHasAddress] = useState(false);

  // استیت فرم مشتری
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    first_name: "",
    last_name: "",
    email: "",
    phone_number: "",
    company: "",
    is_active: true,
  });

  // استیت فرم آدرس
  const [addressData, setAddressData] = useState({
    province_id: "",
    city_id: "",
    postal_code: "",
    address: "",
  });

  // 1. میوتیشن ساخت آدرس
  const addressMutation = useMutation({
    mutationFn: ({ userId, data }) => customerService.createAddress({ userId, addressData: data }),
    onSuccess: () => {
      toast.success("مشتری و آدرس با موفقیت ثبت شدند");
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      navigate("/admin/customers");
    },
    onError: (err) => {
      console.error("Address Error:", err);
      toast.warning("مشتری ساخته شد اما ثبت آدرس با خطا مواجه شد.");
      // حتی اگر آدرس خطا داد، چون مشتری ساخته شده برمی‌گردیم به لیست
      navigate("/admin/customers");
    }
  });

  // 2. میوتیشن ساخت مشتری
  const customerMutation = useMutation({
    mutationFn: customerService.createCustomer,
    onSuccess: (newCustomer) => {
      if (hasAddress) {
        // چک کردن اعتبار داده‌های آدرس قبل از ارسال
        if (!addressData.province_id || !addressData.city_id || !addressData.address) {
             toast.warning("مشتری ساخته شد ولی اطلاعات آدرس ناقص بود.");
             navigate("/admin/customers");
             return;
        }

        // ارسال درخواست ثبت آدرس
        addressMutation.mutate({
            userId: newCustomer.id,
            data: {
                province_id: Number(addressData.province_id),
                city_id: Number(addressData.city_id),
                postal_code: addressData.postal_code || "",
                address: addressData.address
            }
        });
      } else {
        toast.success("مشتری جدید با موفقیت ایجاد شد");
        queryClient.invalidateQueries({ queryKey: ["customers"] });
        navigate("/admin/customers");
      }
    },
    onError: (err) => {
      console.error("Customer Error:", err);
      const msg = err.response?.data?.message || "خطا در ثبت مشتری";
      toast.error(msg);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (hasAddress && (!addressData.province_id || !addressData.city_id)) {
        toast.error("لطفا استان و شهر را انتخاب کنید");
        return;
    }
    customerMutation.mutate(formData);
  };

  const handleInputChange = (e, setFunc) => {
    const { name, value } = e.target;
    setFunc((prev) => ({ ...prev, [name]: value }));
  };

  const isSubmitting = customerMutation.isPending || addressMutation.isPending;

  // اگر اروری در رندرینگ باشد، اینجا هندل می‌شود (Error Boundary ساده)
  try {
      return (
        <div className="max-w-5xl mx-auto p-6 pb-20 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* هدر صفحه */}
          <div className="flex items-center gap-4 mb-8">
            <Button variant="outline" size="icon" type="button" onClick={() => navigate(-1)}>
                <ArrowRight className="h-4 w-4" />
            </Button>
            <div>
                <h1 className="text-2xl font-black text-slate-800">تعریف مشتری جدید</h1>
                <p className="text-slate-500 text-sm">اطلاعات هویتی و آدرس را وارد کنید</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* ستون راست: اطلاعات هویتی */}
            <div className="lg:col-span-7 space-y-6">
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <div className="flex items-center gap-2 mb-6 border-b pb-4">
                        <div className="bg-blue-50 p-2 rounded text-blue-600"><User className="h-5 w-5" /></div>
                        <h2 className="font-bold text-slate-800">اطلاعات کاربری</h2>
                    </div>

                    <div className="grid grid-cols-2 gap-5">
                        <div className="space-y-2">
                            <Label>نام <span className="text-red-500">*</span></Label>
                            <Input name="first_name" value={formData.first_name} onChange={(e) => handleInputChange(e, setFormData)} required />
                        </div>
                        <div className="space-y-2">
                            <Label>نام خانوادگی <span className="text-red-500">*</span></Label>
                            <Input name="last_name" value={formData.last_name} onChange={(e) => handleInputChange(e, setFormData)} required />
                        </div>
                        
                        <div className="space-y-2">
                            <Label>شماره موبایل <span className="text-red-500">*</span></Label>
                            <Input name="phone_number" value={formData.phone_number} onChange={(e) => handleInputChange(e, setFormData)} required className="dir-ltr font-mono" placeholder="0912..." />
                        </div>
                        <div className="space-y-2">
                            <Label>ایمیل (اختیاری)</Label>
                            <Input name="email" type="email" value={formData.email} onChange={(e) => handleInputChange(e, setFormData)} className="dir-ltr font-mono" />
                        </div>

                        <div className="space-y-2">
                            <Label>نام کاربری (انگلیسی) <span className="text-red-500">*</span></Label>
                            <Input name="username" value={formData.username} onChange={(e) => handleInputChange(e, setFormData)} required className="dir-ltr font-mono bg-slate-50" />
                        </div>
                        <div className="space-y-2">
                            <Label>رمز عبور <span className="text-red-500">*</span></Label>
                            <Input name="password" value={formData.password} onChange={(e) => handleInputChange(e, setFormData)} required className="dir-ltr font-mono bg-slate-50" placeholder="حداقل ۸ کاراکتر" />
                        </div>
                    </div>

                    <div className="mt-5 pt-5 border-t">
                        <div className="space-y-2">
                            <Label>نام شرکت / سازمان</Label>
                            <div className="relative">
                                <Building2 className="absolute right-3 top-2.5 h-4 w-4 text-slate-400" />
                                <Input name="company" value={formData.company} onChange={(e) => handleInputChange(e, setFormData)} className="pr-9" placeholder="مثلاً: کانون تبلیغاتی ..." />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ستون چپ: آدرس */}
            <div className="lg:col-span-5 space-y-6">
                <div className={`bg-white p-6 rounded-xl border transition-all duration-300 ${hasAddress ? 'border-gold-dark shadow-md' : 'border-slate-200 shadow-sm opacity-100'}`}>
                    <div className="flex items-center justify-between mb-6 border-b pb-4">
                        <div className="flex items-center gap-2">
                            <div className={`p-2 rounded transition-colors ${hasAddress ? 'bg-gold-light text-gold-dark' : 'bg-slate-100 text-slate-400'}`}>
                                <MapPin className="h-5 w-5" />
                            </div>
                            <h2 className="font-bold text-slate-800">آدرس پستی</h2>
                        </div>
                        <Switch 
                            checked={hasAddress} 
                            onCheckedChange={setHasAddress} 
                        />
                    </div>

                    <div className={`space-y-4 transition-all duration-300 ${hasAddress ? 'opacity-100 pointer-events-auto' : 'opacity-40 pointer-events-none grayscale'}`}>
                        
                        {/* ⭐️ استفاده از کامپوننت جدید انتخاب شهر و استان */}
                        <CitySelector 
                            disabled={!hasAddress}
                            onProvinceChange={(id) => setAddressData(prev => ({ ...prev, province_id: id }))}
                            onCityChange={(id) => setAddressData(prev => ({ ...prev, city_id: id }))}
                        />
                        
                        <div className="space-y-2">
                            <Label>کد پستی</Label>
                            <Input name="postal_code" value={addressData.postal_code} onChange={(e) => handleInputChange(e, setAddressData)} className="font-mono dir-ltr" />
                        </div>

                        <div className="space-y-2">
                            <Label>متن کامل آدرس <span className="text-red-500">*</span></Label>
                            <Textarea 
                                name="address" 
                                value={addressData.address} 
                                onChange={(e) => handleInputChange(e, setAddressData)} 
                                className="min-h-[100px] leading-relaxed" 
                                placeholder="خیابان، کوچه، پلاک..." 
                            />
                        </div>
                    </div>
                    
                    {!hasAddress && (
                        <div className="mt-4 p-3 bg-slate-50 text-slate-500 text-xs rounded text-center flex items-center justify-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            برای ثبت آدرس، سوییچ بالا را روشن کنید.
                        </div>
                    )}
                </div>

                {/* دکمه ذخیره نهایی */}
                <Button 
                    type="submit" 
                    className="w-full h-12 text-base font-bold bg-slate-900 hover:bg-slate-800 text-white shadow-lg shadow-slate-900/20"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? (
                        <>
                            <Loader2 className="ml-2 h-5 w-5 animate-spin" />
                            در حال پردازش...
                        </>
                    ) : (
                        <>
                            <Save className="ml-2 h-5 w-5" />
                            ثبت نهایی مشتری {hasAddress && "+ آدرس"}
                        </>
                    )}
                </Button>
            </div>

          </form>
        </div>
      );
  } catch (error) {
      console.error("Render Error:", error);
      return <div className="p-10 text-center">خطایی در نمایش صفحه رخ داده است. کنسول را چک کنید.</div>;
  }
};

export default CreateCustomer;