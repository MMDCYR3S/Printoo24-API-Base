import os
import sys

# --- لیست‌های فیلتر کردن ---
# 1. پوشه‌هایی که باید به طور کامل مخفی بمانند (نشان داده نمی‌شوند)
HIDDEN_LIST = [
    '.git', '.vscode', '.idea', '.DS_Store', 'venv', '.env'
]

# 2. پوشه‌هایی که فقط نامشان نمایش داده می‌شود، اما محتویاتشان لیست نمی‌شود
IGNORE_CONTENTS_LIST = [
    'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build'
]

def generate_tree(startpath, prefix=''):
    """
    یک تابع بازگشتی برای نمایش ساختار پوشه‌ها و فایل‌ها با قابلیت فیلتر کردن
    """
    try:
        items = sorted(os.listdir(startpath), key=lambda x: (os.path.isfile(os.path.join(startpath, x)), x.lower()))
    except PermissionError:
        # اگر دسترسی به پوشه‌ای وجود نداشت، از آن رد شو
        return

    for index, item in enumerate(items):
        # --- فیلتر کردن ---
        # اگر آیتم در لیست مخفی‌ها بود، آن را کاملاً نادیده بگیر
        if item in HIDDEN_LIST:
            continue

        full_path = os.path.join(startpath, item)
        
        # تعیین کاراکتر اتصال (آخرین آیتم یا نه)
        is_last = (index == len(items) - 1)
        connector = '└── ' if is_last else '├── '
        extension = '    ' if is_last else '│   '

        # چاپ نام آیتم با پیشوند مناسب
        print(f"{prefix}{connector}{item}")

        # اگر آیتم یک پوشه بود
        if os.path.isdir(full_path):
            # اگر پوشه در لیست نادیده گرفتن محتوا بود، وارد آن نشو
            if item in IGNORE_CONTENTS_LIST:
                continue
            # در غیر این صورت، تابع را برای زیرشاخه‌های آن فراخوانی کن
            else:
                generate_tree(full_path, prefix + extension)

if __name__ == "__main__":
    target_directory = sys.argv[1] if len(sys.argv) > 1 else '.'

    if not os.path.isdir(target_directory):
        print(f"خطا: مسیر '{target_directory}' پیدا نشد یا یک پوشه نیست.")
        sys.exit(1)

    print(f"{os.path.basename(os.path.abspath(target_directory))}/")
    generate_tree(target_directory)
