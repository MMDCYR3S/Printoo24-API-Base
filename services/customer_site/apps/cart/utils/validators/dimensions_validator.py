import math
from PIL import Image
from django.core.exceptions import ValidationError

# =========== Validate Image Dimensions =========== #
def validate_image_dimensions(uploaded_file, required_width, required_height):
    """
    ابعاد یک فایل عکس آپلود شده را با ابعاد مورد نیاز (به میلی‌متر) مقایسه می‌کند.
    """
    try:
        uploaded_file.seek(0) 
        with Image.open(uploaded_file) as img:
            width_px, height_px = img.size
            dpi_info = img.info.get("dpi")

            if dpi_info:
                dpi_x, dpi_y = dpi_info
            else:
                raise ValidationError("فایل آپلود شده فاقد اطلاعات رزولوشن (DPI) است.")

            width = (width_px / dpi_x) * 2.54
            height = (height_px / dpi_y) * 2.54

            if not math.isclose(width, required_width, abs_tol=0.5):
                raise ValidationError(
                    f"عرض فایل شما ({round(width, 1)}cm) با عرض مورد نیاز ({required_width}cm) مطابقت ندارد."
                )

            if not math.isclose(height, required_height, abs_tol=0.5):
                raise ValidationError(
                    f"ارتفاع فایل شما ({round(height, 1)}cm) با ارتفاع مورد نیاز ({required_height}cm) مطابقت ندارد."
                )
                
    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError(f"فایل آپلود شده معتبر نیست یا در پردازش آن خطایی رخ داد: {e}")
    finally:
        uploaded_file.seek(0)