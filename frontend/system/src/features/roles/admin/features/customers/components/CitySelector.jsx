import React, { useState, useEffect } from "react";
import { geoService } from "../api/geoService";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

const CitySelector = ({ onProvinceChange, onCityChange, disabled }) => {
  const [provinces, setProvinces] = useState([]);
  const [cities, setCities] = useState([]);
  
  const [selectedProvince, setSelectedProvince] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  
  const [loadingProvinces, setLoadingProvinces] = useState(false);
  const [loadingCities, setLoadingCities] = useState(false);

  // لود کردن استان‌ها در شروع کار
  useEffect(() => {
    const fetchProvinces = async () => {
      setLoadingProvinces(true);
      try {
        const data = await geoService.getProvinces();
        setProvinces(data);
      } catch (error) {
        console.error("خطا در دریافت استان‌ها", error);
      } finally {
        setLoadingProvinces(false);
      }
    };
    fetchProvinces();
  }, []);

  // هندل کردن تغییر استان
  const handleProvinceChange = async (e) => {
    const provinceId = e.target.value;
    setSelectedProvince(provinceId);
    setSelectedCity(""); // ریست کردن شهر
    onProvinceChange(provinceId); // اطلاع به فرم پدر
    onCityChange(""); 

    if (provinceId) {
      setLoadingCities(true);
      try {
        const data = await geoService.getCities(provinceId);
        setCities(data);
      } catch (error) {
        console.error("خطا در دریافت شهرها", error);
      } finally {
        setLoadingCities(false);
      }
    } else {
      setCities([]);
    }
  };

  // هندل کردن تغییر شهر
  const handleCityChange = (e) => {
    const cityId = e.target.value;
    setSelectedCity(cityId);
    onCityChange(cityId);
  };

  // کلاس استایل مشترک برای اینپوت‌ها
  const selectClass = "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label>استان <span className="text-red-500">*</span></Label>
        <div className="relative">
            <select 
                value={selectedProvince} 
                onChange={handleProvinceChange} 
                className={selectClass}
                disabled={disabled || loadingProvinces}
            >
                <option value="">انتخاب استان...</option>
                {provinces.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                ))}
            </select>
            {loadingProvinces && <Loader2 className="absolute left-3 top-2.5 h-4 w-4 animate-spin text-slate-400" />}
        </div>
      </div>

      <div className="space-y-2">
        <Label>شهر <span className="text-red-500">*</span></Label>
        <div className="relative">
            <select 
                value={selectedCity} 
                onChange={handleCityChange} 
                className={selectClass}
                disabled={disabled || !selectedProvince || loadingCities}
            >
                <option value="">انتخاب شهر...</option>
                {cities.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                ))}
            </select>
            {loadingCities && <Loader2 className="absolute left-3 top-2.5 h-4 w-4 animate-spin text-slate-400" />}
        </div>
      </div>
    </div>
  );
};

export default CitySelector;