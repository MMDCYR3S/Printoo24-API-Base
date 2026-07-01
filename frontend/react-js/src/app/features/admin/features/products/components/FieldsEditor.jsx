import React, { useState } from "react";
import { useFormContext, useFieldArray } from "react-hook-form";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
  arrayMove,
} from "@dnd-kit/sortable";
import { Settings, Plus, Sparkles } from "lucide-react";
import { generateTempId } from "../../../hooks/useStep2Form";

import SortableFieldItem from "./SortableFieldItem"; // کامپوننتی که در ادامه می‌سازیم

const FieldsEditor = () => {
  const [expandedIndex, setExpandedIndex] = useState(0);
  const { control } = useFormContext();

  const { fields, append, remove, move } = useFieldArray({
    control,
    name: "fields",
  });

  // تنظیمات سنسورهای درگ و دراپ (تا با کلیک‌های معمولی تداخل نداشته باشد)
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5, // کاربر باید ۵ پیکسل موس را بکشد تا درگ شروع شود
      },
    }),
  );

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      const oldIndex = fields.findIndex(
        (f) => (f.id || f.temp_id) === active.id,
      );
      const newIndex = fields.findIndex((f) => (f.id || f.temp_id) === over.id);
      move(oldIndex, newIndex);
    }
  };

  const handleAddField = () => {
    append({
      id: null,
      temp_id: generateTempId("field"),
      title: "",
      field_type: "dropdown",
      is_required: false,
      choices: [],
      conditions: [],
    });
    setExpandedIndex(fields.length); // باز کردن آکاردئون فیلد جدید
  };

  return (
    <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 rounded-[2rem]">
      {/* هدر بخش فرم‌ساز */}
      <div className="flex justify-between items-start mb-8">
        <div className="flex items-start gap-5">
          <div className="w-14 h-14 rounded-[1.25rem] bg-gradient-to-br from-blue-500/10 to-blue-500/5 flex items-center justify-center text-blue-600 shadow-sm border border-blue-500/10">
            <Settings size={26} strokeWidth={1.5} />
          </div>
          <div>
            <h3 className="font-extrabold text-slate-800 text-2xl tracking-tight">
              ساختار فرم (فیلدها)
            </h3>
            <p className="text-sm text-slate-500 mt-2 font-medium">
              فیلدهای محصول و شروط نمایش آن‌ها را مدیریت کنید.
            </p>
          </div>
        </div>
        <button
          onClick={handleAddField}
          type="button"
          className="btn btn-primary btn-sm rounded-full shadow-lg shadow-primary/20 hover:scale-105 px-6"
        >
          <Plus size={16} /> فیلد جدید
        </button>
      </div>

      {/* لیست فیلدها با درگ و دراپ */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={fields.map((f) => f.id || f.temp_id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-5">
            {fields.map((field, index) => {
              const uniqueId = field.id || field.temp_id;
              return (
                <SortableFieldItem
                  key={uniqueId}
                  id={uniqueId}
                  index={index}
                  expanded={expandedIndex === index}
                  onToggle={() =>
                    setExpandedIndex(expandedIndex === index ? null : index)
                  }
                  onRemove={() => remove(index)}
                />
              );
            })}
          </div>
        </SortableContext>
      </DndContext>

      {/* وضعیت خالی */}
      {fields.length === 0 && (
        <div className="flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-200 rounded-[2rem] bg-slate-50/50 py-16 mt-4">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
            <Sparkles className="text-blue-500/40" size={36} />
          </div>
          <h4 className="font-extrabold text-slate-600 text-lg">
            هنوز فیلدی اضافه نکرده‌اید
          </h4>
          <button
            onClick={handleAddField}
            type="button"
            className="btn btn-outline btn-primary rounded-full px-8 mt-6"
          >
            ساخت اولین فیلد
          </button>
        </div>
      )}
    </div>
  );
};

export default FieldsEditor;
