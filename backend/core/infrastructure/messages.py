# core/infrastructure/messages.py

import json
import os
from django.conf import settings
from functools import lru_cache

class MessageProvider:
    @staticmethod
    @lru_cache(maxsize=1)
    def _load_messages():
        """بارگذاری فایل JSON با استفاده از سیستم کش برای پرفورمنس بالا"""
        file_path = getattr(settings, 'MESSAGES_JSON_FILE', os.path.join(settings.BASE_DIR, 'locale/messages.json'))
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def get(cls, dot_key: str, **kwargs):
        """
        دریافت پیام و جایگذاری متغیرهای داینامیک.
        مثال: msg_provider.get("cart.E4006", min_qty=10)
        خروجی: {"code": "E4006", "text": "حداقل تعداد سفارش 10 عدد است.", "type": "error"}
        """
        keys = dot_key.split('.')
        code = keys[-1]
        
        data = cls._load_messages()
        # پیمایش درختی در فایل JSON
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                data = None
                break
        
        # اگر پیام پیدا نشد، کد را برمی‌گردانیم
        text = data or "پیام تعریف نشده است"
        
        # عملیات Formatting: جایگذاری متغیرها در متن
        if isinstance(text, str) and kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                # در صورتی که متغیری در متن باشد ولی در kwargs فرستاده نشده باشد
                text = f"{text} (خطا در پارامتر: {str(e)})"

        # تعیین نوع پیام بر اساس کد (E=Error, S=Success, I=Info)
        msg_type = "success" if code.startswith('S') else "error"
        if code.startswith('I'): msg_type = "info"

        return {
            "code": code,
            "text": text,
            "type": msg_type
        }

msg_provider = MessageProvider()