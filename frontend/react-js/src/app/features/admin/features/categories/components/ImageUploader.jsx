// src/app/components/inputs/ImageUploader.jsx
import React, { useState, useEffect } from 'react';
import { UploadCloud, X, Image as ImageIcon } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import clsx from 'clsx';

const ImageUploader = ({ label, defaultImage, onChange, error, aspectRatio = "square" }) => {
  const [preview, setPreview] = useState(defaultImage);

  // اگر مقدار اولیه تغییر کرد (مثلاً بعد از لود دیتا در حالت ادیت)
  useEffect(() => {
    if (typeof defaultImage === 'string') setPreview(defaultImage);
  }, [defaultImage]);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setPreview(URL.createObjectURL(file));
      onChange(file); // فایل واقعی را به فرم می‌دهیم
    }
  };

  const removeImage = (e) => {
    e.stopPropagation();
    setPreview(null);
    onChange(null); // مقدار را خالی می‌کنیم
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpeg', '.png', '.jpg', '.webp'] },
    maxFiles: 1,
    multiple: false
  });

  return (
    <div className="form-control w-full">
      <label className="label font-bold text-slate-700 text-sm mb-2">{label}</label>
      
      <div
        {...getRootProps()}
        className={clsx(
          "relative border-2 border-dashed rounded-2xl transition-all duration-300 cursor-pointer overflow-hidden group",
          isDragActive ? "border-primary bg-primary/5" : "border-slate-300 hover:border-primary hover:bg-slate-50",
          error ? "border-error" : "",
          aspectRatio === 'wide' ? 'aspect-[3/1]' : 'aspect-square'
        )}
      >
        <input {...getInputProps()} />

        {preview ? (
          <div className="relative w-full h-full">
            <img src={preview} alt="Preview" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
              <p className="text-white font-bold text-sm">تغییر تصویر</p>
            </div>
            <button
              onClick={removeImage}
              type="button"
              className="absolute top-2 left-2 btn btn-circle btn-xs btn-error text-white shadow-lg"
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
            <div className={clsx("p-3 rounded-full bg-slate-100 transition-colors group-hover:bg-primary/10 group-hover:text-primary")}>
              <UploadCloud size={24} />
            </div>
            <div className="text-center px-4">
              <p className="text-xs font-bold text-slate-600">کلیک یا رها کردن عکس</p>
              <p className="text-[10px] mt-1 opacity-60">JPG, PNG (Max 2MB)</p>
            </div>
          </div>
        )}
      </div>
      {error && <span className="text-error text-xs mt-1">{error.message}</span>}
    </div>
  );
};

export default ImageUploader;