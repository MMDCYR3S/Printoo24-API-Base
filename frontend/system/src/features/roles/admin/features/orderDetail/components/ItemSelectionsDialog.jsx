import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Settings2, Plus, X } from "lucide-react";

// این کامپوننت یک آبجکت ساده میگیره و اجازه میده کلید-مقدار بهش اضافه کنی
const ItemSelectionsDialog = ({ value = {}, onChange }) => {
  const [open, setOpen] = useState(false);
  // تبدیل آبجکت به آرایه برای نمایش در فرم
  const [attributes, setAttributes] = useState(
    Object.entries(value).map(([k, v]) => ({ key: k, value: v }))
  );

  const handleSave = () => {
    // تبدیل آرایه به آبجکت برای ذخیره در فرم اصلی
    const newSelections = attributes.reduce((acc, curr) => {
        if (curr.key) acc[curr.key] = curr.value;
        return acc;
    }, {});
    onChange(newSelections);
    setOpen(false);
  };

  const addAttribute = () => setAttributes([...attributes, { key: "", value: "" }]);
  const removeAttribute = (idx) => setAttributes(attributes.filter((_, i) => i !== idx));
  
  const updateAttribute = (idx, field, val) => {
      const newAttrs = [...attributes];
      newAttrs[idx][field] = val;
      setAttributes(newAttrs);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant={Object.keys(value).length > 0 ? "default" : "outline"} size="sm" className="h-8">
          <Settings2 className="w-3 h-3 mr-2" />
          {Object.keys(value).length > 0 ? `${Object.keys(value).length} ویژگی` : "ویژگی‌ها"}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>ویژگی‌های محصول (Selections)</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <p className="text-sm text-muted-foreground">ویژگی‌هایی مثل جنس کاغذ، رنگ، روکش و... را وارد کنید.</p>
          
          {attributes.map((attr, index) => (
            <div key={index} className="flex items-center gap-2">
                <Input 
                    placeholder="عنوان (مثلا: کاغذ)" 
                    value={attr.key}
                    onChange={(e) => updateAttribute(index, "key", e.target.value)}
                    className="w-1/3"
                />
                <Input 
                    placeholder="مقدار (مثلا: گلاسه)" 
                    value={attr.value}
                    onChange={(e) => updateAttribute(index, "value", e.target.value)}
                    className="w-full"
                />
                <Button variant="ghost" size="icon" onClick={() => removeAttribute(index)}>
                    <X className="w-4 h-4 text-red-500" />
                </Button>
            </div>
          ))}

          <Button type="button" variant="outline" size="sm" onClick={addAttribute} className="mt-2 border-dashed">
            <Plus className="w-4 h-4 mr-2" /> افزودن ویژگی جدید
          </Button>
        </div>
        <DialogFooter>
          <Button onClick={handleSave}>ذخیره تغییرات</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ItemSelectionsDialog;