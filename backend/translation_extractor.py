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
            'HttpResponseServerError', 'HttpResponseForbidden',
            'HttpResponseNotAllowed', 'HttpResponseGone', 
            'HttpResponsePermanentRedirect', 'HttpResponseRedirect'
        }

    def _extract_strings(self, node):
        """استخراج تمام رشته‌های متنی از یک نود (حتی در دیکشنری‌ها، لیست‌ها و f-string ها)"""
        messages = []
        if node is None:
            return messages
            
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value.strip(): # نادیده گرفتن رشته‌های کاملاً خالی
                messages.append(node.value)
        elif isinstance(node, ast.JoinedStr): # برای f-string ها
            for value in node.values:
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    if value.value.strip():
                        messages.append(value.value)
        elif isinstance(node, ast.Dict):
            for v in node.values:
                messages.extend(self._extract_strings(v))
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
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
                
                messages = []
                for arg in node.exc.args:
                    messages.extend(self._extract_strings(arg))
                for kw in node.exc.keywords:
                    messages.extend(self._extract_strings(kw))
                    
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
        """شناسایی تمام Response های کلاسیک (مثل JsonResponse یا Response)"""
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in self.response_classes:
            messages = []
            for arg in node.args:
                messages.extend(self._extract_strings(arg))
            for kw in node.keywords:
                messages.extend(self._extract_strings(kw))

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
        
    def visit_Return(self, node):
        """شناسایی تمام return هایی که مستقیماً مقدار متنی، دیکشنری یا لیست برمی‌گردانند"""
        if node.value:
            # بررسی می‌کنیم که آیا return مستقیماً یک کلاس Response را صدا می‌زند یا خیر
            # اگر Response صدا بزند، توسط visit_Call هندل می‌شود تا دوگانگی ایجاد نشود
            is_response_call = False
            if isinstance(node.value, ast.Call):
                func_name = ""
                if isinstance(node.value.func, ast.Name):
                    func_name = node.value.func.id
                elif isinstance(node.value.func, ast.Attribute):
                    func_name = node.value.func.attr
                if func_name in self.response_classes:
                    is_response_call = True
            
            # اگر Response نباشد، بررسی می‌کنیم که آیا رشته‌ای در خروجی return وجود دارد یا خیر
            if not is_response_call:
                messages = self._extract_strings(node.value)
                for msg in messages:
                    self.results.append({
                        'type': 'Return',
                        'class': 'DirectReturn',
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
    parser = argparse.ArgumentParser(description="استخراج Response ها، Exception ها و Return ها برای ترجمه")
    parser.add_argument('--dirs', nargs='+', default=['customer_site', 'shared_libs'], 
                        help="نام پوشه‌هایی که باید اسکن شوند")
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

    # ذخیره در فایل CSV
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