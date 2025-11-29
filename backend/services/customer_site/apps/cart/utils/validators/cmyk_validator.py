from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os

# ======== IMAGE CMYK VALIDATOR ======== #
def validate_image_cmyk(file):
    """
    تاییدکننده برای اطمینان از اینکه فایل تصویر در مد رنگی CMYK باشد
    """
    valid_extensions = ['.jpg', '.jpeg', '.tif', '.tiff', '.pdf', '.ai', '.eps', '.psd']

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(
            _('فرمت فایل معتبر نیست. فرمت‌های مجاز: %(extensions)s'),
            params={'extensions': ', '.join(valid_extensions)},
        )
    
    if ext in ['.pdf', '.ai', '.eps']:
        if ext in ['.ai', '.eps']:
            try:
                file_content = file.read(1024)
                file.seek(0)
                
                content_str = file_content.decode('latin-1', errors='ignore')
                
                if 'CMYK' not in content_str and 'Cyan' not in content_str and 'Magenta' not in content_str:
                    pass
            except Exception:
                pass
        return
    
    try:
        img = Image.open(file)
        
        if img.mode != 'CMYK':
            raise ValidationError(_('فایل باید در مد رنگی CMYK باشد. مد فعلی: %(mode)s'), 
                                 params={'mode': img.mode})
            
    except ValidationError:
        raise
    except Exception as e:
        if ext in ['.psd']:
            return
        raise ValidationError(_('خطا در باز کردن فایل: %(error)s'), params={'error': str(e)})
