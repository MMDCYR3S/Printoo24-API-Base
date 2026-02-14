import React, { useState, useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { useCustomerSearch, useCustomerAddresses } from "../../customers/hooks/useCustomers";
import { useProvinces, useCities } from "@/features/shared/geo/hooks/useGeo"; // هوک‌های جدید
import QuickCustomerModal from "./QuickCustomerModal";

// UI Components
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"; // نیاز به فایل Tabs داریم
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, PlusCircle, Navigation } from "lucide-react";

const OrderCustomerSection = () => {
  const { control, setValue, watch } = useFormContext();
  
  // State
  const selectedUserId = watch("user_id");
  const [addressMode, setAddressMode] = useState("saved"); // 'saved' | 'new'
  const [selectedProvince, setSelectedProvince] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [postalCode, setPostalCode] = useState("");
  const [addressDetail, setAddressDetail] = useState("");

  // Queries
  const { data: customers, isLoading: loadingCustomers, refetch } = useCustomerSearch("");
  const { data: addresses, isLoading: loadingAddresses } = useCustomerAddresses(selectedUserId);
  const { data: provinces, isLoading: loadingProvinces } = useProvinces();
  const { data: cities, isLoading: loadingCities } = useCities(selectedProvince);

  // --- Handlers ---

  // 1. انتخاب مشتری
  const onCustomerSelect = (customerId) => {
    const customer = customers?.find(c => c.id.toString() === customerId);
    if (customer) {
        setValue("user_id", customer.id);
        setValue("recipient_name", `${customer.first_name} ${customer.last_name}`);
        setValue("recipient_phone", customer.phone_number);
        setValue("full_address", "");
        setAddressMode("saved"); // ریست به حالت پیش‌فرض
    }
  };

  // 2. انتخاب از لیست ذخیره شده
  const onSavedAddressSelect = (addressId) => {
      const address = addresses?.find(a => a.id.toString() === addressId);
      if (address) {
          const fullString = `${address.province} - ${address.city} - ${address.address} ${address.postal_code ? `(کدپستی: ${address.postal_code})` : ''}`;
          setValue("full_address", fullString);
      }
  };

  // 3. ساخت آدرس دستی (ترکیب استان + شهر + جزئیات)
  useEffect(() => {
    if (addressMode === "new" && selectedProvince && selectedCity && addressDetail) {
        const provinceName = provinces?.find(p => p.id.toString() === selectedProvince)?.name || "";
        const cityName = cities?.find(c => c.id.toString() === selectedCity)?.name || "";
        
        const fullString = `${provinceName} - ${cityName} - ${addressDetail} ${postalCode ? `(کدپستی: ${postalCode})` : ''}`;
        setValue("full_address", fullString);
    }
  }, [selectedProvince, selectedCity, addressDetail, postalCode, addressMode]);

  // ثبت مشتری جدید
  const handleNewCustomer = (newCustomer) => {
      refetch().then(() => {
          onCustomerSelect(newCustomer.id.toString());
      });
  };

  return (
    <Card className="mb-6 border-l-4 border-l-blue-600">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-bold flex justify-between items-center">
          <span>مشتری و مقصد سفارش</span>
          <QuickCustomerModal onCustomerCreated={handleNewCustomer} />
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        
        {/* ردیف اول: انتخاب مشتری */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              control={control}
              name="user_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>انتخاب مشتری <span className="text-red-500">*</span></FormLabel>
                  <Select
                    disabled={loadingCustomers}
                    onValueChange={(val) => { field.onChange(val); onCustomerSelect(val); }}
                    value={field.value?.toString()}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="جستجوی مشتری..." />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {customers?.map((customer) => (
                        <SelectItem key={customer.id} value={customer.id.toString()}>
                          {customer.first_name} {customer.last_name} - {customer.company || customer.phone_number}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormItem>
              )}
            />

            {/* فیلد گیرنده (فقط نمایشی/ویرایشی) */}
            <FormField
              control={control} name="recipient_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>نام تحویل گیرنده</FormLabel>
                  <Input {...field} />
                </FormItem>
              )}
            />
        </div>

        {/* بخش آدرس (تب‌بندی شده) */}
        <div className="p-4 border rounded-lg bg-muted/10">
            <Label className="mb-2 block font-semibold">اطلاعات آدرس</Label>
            
            <Tabs value={addressMode} onValueChange={setAddressMode} className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-4">
                    <TabsTrigger value="saved" disabled={!selectedUserId}>آدرس‌های ذخیره شده</TabsTrigger>
                    <TabsTrigger value="new">آدرس جدید (دستی)</TabsTrigger>
                </TabsList>

                {/* تب ۱: آدرس‌های ذخیره شده */}
                <TabsContent value="saved">
                    <FormItem>
                        <Select onValueChange={onSavedAddressSelect} disabled={!selectedUserId || loadingAddresses}>
                            <SelectTrigger>
                                <SelectValue placeholder={!selectedUserId ? "ابتدا مشتری را انتخاب کنید" : "انتخاب یکی از آدرس‌های مشتری"} />
                            </SelectTrigger>
                            <SelectContent>
                                {addresses?.map((addr) => (
                                    <SelectItem key={addr.id} value={addr.id.toString()}>
                                        <span className="flex items-center">
                                            <MapPin className="w-3 h-3 mr-2 text-muted-foreground" />
                                            {addr.province}، {addr.city} - {addr.address}
                                        </span>
                                    </SelectItem>
                                ))}
                                {addresses?.length === 0 && <div className="p-2 text-sm text-center text-muted-foreground">آدرسی یافت نشد</div>}
                            </SelectContent>
                        </Select>
                    </FormItem>
                </TabsContent>

                {/* تب ۲: آدرس جدید (استان/شهر) */}
                <TabsContent value="new" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        {/* انتخاب استان */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">استان</label>
                            <Select onValueChange={setSelectedProvince} value={selectedProvince}>
                                <SelectTrigger>
                                    <SelectValue placeholder="انتخاب استان" />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px]">
                                    {provinces?.map((p) => (
                                        <SelectItem key={p.id} value={p.id.toString()}>{p.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* انتخاب شهر (وابسته به استان) */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">شهر</label>
                            <Select 
                                onValueChange={setSelectedCity} 
                                value={selectedCity} 
                                disabled={!selectedProvince || loadingCities}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder={loadingCities ? "در حال دریافت..." : "انتخاب شهر"} />
                                </SelectTrigger>
                                <SelectContent className="max-h-[200px]">
                                    {cities?.map((c) => (
                                        <SelectItem key={c.id} value={c.id.toString()}>{c.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4">
                        <div className="col-span-3 space-y-2">
                            <label className="text-sm font-medium">جزئیات آدرس (خیابان، پلاک...)</label>
                            <Input 
                                placeholder="آدرس دقیق..." 
                                value={addressDetail}
                                onChange={(e) => setAddressDetail(e.target.value)}
                            />
                        </div>
                        <div className="col-span-1 space-y-2">
                            <label className="text-sm font-medium">کد پستی</label>
                            <Input 
                                placeholder="اختیاری" 
                                value={postalCode}
                                onChange={(e) => setPostalCode(e.target.value)}
                            />
                        </div>
                    </div>
                </TabsContent>
            </Tabs>
        </div>

        {/* نمایش نهایی آدرس (فقط خواندنی یا قابل ویرایش نهایی) */}
        <FormField
          control={control} name="full_address"
          render={({ field }) => (
            <FormItem>
              <FormLabel>آدرس نهایی (قابل ارسال)</FormLabel>
              <FormControl>
                <Input className="bg-muted/50" readOnly={false} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </CardContent>
    </Card>
  );
};

// کامپوننت Label کمکی
const Label = ({ children, className }) => <label className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}>{children}</label>;

export default OrderCustomerSection;