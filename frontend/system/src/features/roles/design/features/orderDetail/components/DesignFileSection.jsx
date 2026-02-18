import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileIcon, Download, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DesignFileSection({ files }) {
  if (!files || files.length === 0) return null;

  return (
    <Card className="border-slate-100 shadow-sm">
      <CardHeader className="py-4 border-b border-slate-50 bg-slate-50/50">
        <CardTitle className="text-sm font-black flex items-center gap-2">
          <FileIcon className="h-4 w-4 text-gold-dark" />
          فایل‌های ارسالی و ضمایم
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-1 gap-3">
          {files.map((file) => (
            <div key={file.id} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-white hover:bg-slate-50 transition-colors group">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-100 rounded-md text-slate-500 group-hover:bg-white group-hover:shadow-sm">
                  <FileIcon size={18} />
                </div>
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-slate-700 truncate max-w-[200px]" dir="ltr">
                    {file.filename}
                  </span>
                  <span className="text-[10px] text-slate-400">نسخه: {file.version}</span>
                </div>
              </div>
              <div className="flex gap-1">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" asChild>
                  <a href={file.file_url} target="_blank" rel="noreferrer"><ExternalLink size={14} /></a>
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-blue-600 hover:text-blue-700 hover:bg-blue-50" asChild>
                  <a href={file.file_url} download><Download size={14} /></a>
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}