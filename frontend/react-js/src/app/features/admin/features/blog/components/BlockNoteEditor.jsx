// src/app/features/admin/articles/components/BlockNoteEditor.jsx
import React, { useEffect } from 'react';
import { useCreateBlockNote } from "@blocknote/react";
import { BlockNoteView } from "@blocknote/mantine"; // <--- تغییر مهم
import "@blocknote/core/fonts/inter.css";
import "@blocknote/mantine/style.css"; // <--- تغییر مهم

const BlockNoteEditor = ({ initialHTML, onChange }) => {
  const editor = useCreateBlockNote();

  useEffect(() => {
    if (initialHTML && editor) {
      async function loadInitialHTML() {
        const blocks = await editor.tryParseHTMLToBlocks(initialHTML);
        editor.replaceBlocks(editor.document, blocks);
      }
      loadInitialHTML();
    }
  }, [initialHTML, editor]);

  return (
    <div className="border border-slate-200 rounded-2xl overflow-hidden bg-slate-50 focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all shadow-inner relative min-h-[400px]">
      <div dir="rtl" className="h-full w-full py-4 text-right">
        <BlockNoteView 
          editor={editor} 
          theme="light"
          onChange={() => {
            const getHTML = async () => {
              const html = await editor.blocksToHTMLLossy(editor.document);
              onChange(html);
            };
            getHTML();
          }}
        />
      </div>
    </div>
  );
};

export default BlockNoteEditor;