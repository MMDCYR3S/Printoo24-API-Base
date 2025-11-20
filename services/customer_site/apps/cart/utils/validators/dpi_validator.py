from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os

# ======== IMAGE DPI VALIDATOR ======== #

def validate_image_dpi(file):
    """
    تاییدکننده برای اطمینان از اینکه فایل تصویر حداقل رزولوشن 300 DPI را داشته باشد
    """
    min_dpi = 300
    valid_extensions = ['.jpg', '.jpeg', '.tif', '.tiff', '.pdf', '.ai', '.eps', '.psd']

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in valid_extensions:
        return
    
    if ext in ['.pdf', '.ai', '.eps']:
        file_size = file.size
        if file_size < 10 * 1024:
            raise ValidationError(_('حجم فایل بسیار کم است و ممکن است کیفیت مناسبی نداشته باشد.'))
        return
    
    try:
        img = Image.open(file)

        dpi_found = False
        if hasattr(img, 'info') and 'dpi' in img.info:
            dpi = img.info['dpi']
            dpi_found = True
            if min(dpi) < min_dpi:
                raise ValidationError(_(f'رزولوشن تصویر باید حداقل {min_dpi} DPI باشد. رزولوشن فعلی: {min(dpi)} DPI'))
        
        if not dpi_found and hasattr(img, 'size'):
            width_px, height_px = img.size
            
            estimated_dpi = min(width_px / 3.5, height_px / 3.5)
            
            if estimated_dpi < min_dpi:
                raise ValidationError(_(f'ابعاد تصویر برای چاپ با کیفیت کافی نیست. رزولوشن تخمینی: {int(estimated_dpi)} DPI'))
            
    except ValidationError:
        raise
    except Exception as e:
        if ext in ['.psd']:
            return
        raise ValidationError(_('خطا در باز کردن فایل: %(error)s'), params={'error': str(e)})