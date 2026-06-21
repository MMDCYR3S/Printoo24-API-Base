import os
import ast
import csv
import argparse
from pathlib import Path

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self, filepath, source_code):
        self.filepath = filepath
        self.source_code = source_code
        self.results = []
        
        # کلاس‌هایی که به عنوان Response شناخته می‌شوند
        self.response_classes = {
            'Response', 'HttpResponse', 'JsonResponse', 
            'HttpResponseNotFound', 'HttpResponseBadRequest', 
            'HttpResponseServerError', 'HttpResponseForbidden'
        }

    def _extract_strings(self, node):
        """استخراج تمام رشته‌های متنی از یک نود (حتی در دیکشنری‌ها و لیست‌ها)"""
        messages = []
        
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            messages.append(node.value)
        elif isinstance(node, ast.JoinedStr): # برای f-string ها
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    messages.append(value.value)
        elif isinstance(node, ast.Dict):
            for v in node.values:
                messages.extend(self._extract_strings(v))
        elif isinstance(node, (ast.List, ast.Tuple)):
            for elt in node.elts:
                messages.extend(self._extract_strings(elt))
        elif isinstance(node, ast.keyword):
            messages.extend(self._extract_strings(node.value))
                
        return messages

    def visit_Raise(self, node):
        """شناسایی تمام Exception های raise شده"""
        if node.exc:
            exc_name = "Unknown"
            if isinstance(node.exc, ast.Call):
                if isinstance(node.exc.func, ast.Name):
                    exc_name = node.exc.func.id
                elif isinstance(node.exc.func, ast.Attribute):
                    exc_name = node.exc.func.attr
                
                # استخراج پیام‌های متنی داخل exception
                messages = []
                for arg in node.exc.args:
                    messages.extend(self._extract_strings(arg))
                    
                if messages:
                    for msg in messages:
                        self.results.append({
                            'type': 'Exception',
                            'class': exc_name,
                            'message': msg,
                            'file': self.filepath,
                            'line': node.lineno,
                            'code': ast.get_source_segment(self.source_code, node).strip()
                        })
                        
        self.generic_visit(node)

    def visit_Call(self, node):
        """شناسایی تمام Response های برگردانده شده"""
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in self.response_classes:
            messages = []
            # بررسی آرگومان‌های ورودی به Response
            for arg in node.args:
                messages.extend(self._extract_strings(arg))
            # بررسی keyword arguments (مثل data={'msg': '...'})
            for kw in node.keywords:
                messages.extend(self._extract_strings(kw))

            if messages:
                for msg in messages:
                    self.results.append({
                        'type': 'Response',
                        'class': func_name,
                        'message': msg,
                        'file': self.filepath,
                        'line': node.lineno,
                        'code': ast.get_source_segment(self.source_code, node).strip()
                    })
                    
        self.generic_visit(node)

def analyze_directory(directory):
    all_results = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"⚠️ مسیر یافت نشد: {directory}")
        return []

    # پیدا کردن تمام فایل‌های پایتون به جز migrations و pycache
    for filepath in dir_path.rglob("*.py"):
        if "migrations" in filepath.parts or "__pycache__" in filepath.parts:
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(filepath))
            analyzer = CodeAnalyzer(str(filepath), source)
            analyzer.visit(tree)
            all_results.extend(analyzer.results)
        except Exception as e:
            print(f"❌ خطا در پردازش فایل {filepath}: {e}")
            
    return all_results

def main():
    parser = argparse.ArgumentParser(description="استخراج Response ها و Exception ها برای ترجمه")
    parser.add_argument('--dirs', nargs='+', default=['customer_site', 'shared_libs'], 
                        help="نام پوشه‌هایی که باید اسکن شوند (پیش‌فرض: customer_site shared_libs)")
    args = parser.parse_args()

    print("🔍 در حال اسکن پروژه برای یافتن پیام‌ها...")
    
    all_results = []
    for d in args.dirs:
        print(f"📁 اسکن پوشه: {d}")
        all_results.extend(analyze_directory(d))

    # چاپ نتایج در ترمینال
    print(f"\n✅ مجموع {len(all_results)} مورد یافت شد.\n")
    print("=" * 80)
    for item in all_results:
        print(f"[{item['type']}] {item['class']}")
        print(f"📝 Message : {item['message']}")
        print(f"📂 File    : {item['file']}")
        print(f"🔢 Line    : {item['line']}")
        print(f"💻 Code    : {item['code']}")
        print("-" * 80)

    # ذخیره در فایل CSV برای استفاده در فرآیند ترجمه
    csv_file = "translation_report.csv"
    if all_results:
        with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['type', 'class', 'message', 'file', 'line', 'code'])
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n📊 خروجی در فایل {csv_file} ذخیره شد.")
    else:
        print("\n⚠️ هیچ پیامی برای ذخیره یافت نشد.")

if __name__ == "__main__":
    main()