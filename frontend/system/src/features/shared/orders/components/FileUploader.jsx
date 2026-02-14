import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone"; // نیاز به نصب: npm install react-dropzone
import { UploadCloud, X, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

const FileUploader = ({ value = [], onChange }) => {
  const onDrop = useCallback((acceptedFiles) => {
    // در اینجا باید لاجیک آپلود به سرور باشد، فعلا فایل‌ها را نگه می‌داریم
    onChange([...value, ...acceptedFiles]);
  }, [value, onChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const removeFile = (index) => {
    const newFiles = [...value];
    newFiles.splice(index, 1);
    onChange(newFiles);
  };

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 transition-colors cursor-pointer flex flex-col items-center justify-center ${
          isDragActive ? "border-primary bg-primary/5" : "border-muted"
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-8 h-8 text-muted-foreground mb-2" />
        <p className="text-xs text-muted-foreground">فایل‌های طرح را اینجا رها کنید</p>
      </div>

      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((file, idx) => (
            <div key={idx} className="flex items-center bg-muted p-1 px-2 rounded text-[10px] gap-2">
              <FileText size={12} />
              <span className="truncate max-w-[100px]">{file.name || "فایل"}</span>
              <button onClick={() => removeFile(idx)} className="text-destructive"><X size={12} /></button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUploader;