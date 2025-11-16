from typing import Dict

from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from shared_libs.core.core.models import Product, CartItemUpload

# ====== Cart File Handler Service ====== #
class CartFileHandlerService:
    """
    سرویس مدیریت فایل‌های آپلود شده برای هر آیتم سبد خرید
    """
    
    def handle_uploads(self, cart_item_id: int, product: Product, files: Dict[str, UploadedFile]):
        """
        بررسی اینکه آیا تمامی عکس های مورد نیاز برای محصول آپلود شده است یا خیر
        """
        required_files = product.file_upload_requirements.all()
        
        # ===== اگر نیازی به آپلود نبود و آپلود انجام شد ===== #
        # ===== نکته: این بخش صرفاً برای صحیح بودن منطق کلی سیستم است. ===== #
        if not required_files and files:
            raise ValidationError("این محصول نیازمند فایل طراحی نیست.")
        
        # ===== بررسی و اعتبارسنجی آپلود فایل ===== #
        for req in required_files:
            uploaded_file = files.get(str(req.id))
            
            if req.is_required and not uploaded_file:
                raise ValidationError(f"فایل {req.spec.name} باید آپلود شود.")
            
            if uploaded_file:
                CartItemUpload.objects.create(
                    cart_item=cart_item_id,
                    requirement=req,
                    file=uploaded_file
                )
