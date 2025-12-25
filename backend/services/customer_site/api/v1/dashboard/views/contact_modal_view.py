from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

# ===== فراخوانی سرویس و مدل‌ها از Shared Libs ===== #
from apps.home.services import ContactService, ModalService
from apps.home.models import ContactUs, PromotionalModal
from ..serializers.general_serializers import (
    ContactUsSerializer,
    PromotionalModalSerializer,
    ReplyMessageSerializer
)

# ===== ویو مدیریت تماس با ما ===== #
# ===== ویو مدیریت تماس با ما (مخصوص ادمین) ===== #
@extend_schema(tags=['Dashboard-Contact-Us'])
class ContactUsViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """
    مدیریت پیام‌های تماس با ما در داشبورد ادمین.
    عملیات مجاز: مشاهده لیست، مشاهده جزئیات، حذف پیام، و پاسخ دادن.
    نکته: ایجاد پیام (Create) در اینجا وجود ندارد چون مربوط به سایت مشتری است.
    """
    queryset = ContactUs.objects.all().order_by('-created_at')
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ContactService()

    def retrieve(self, request, *args, **kwargs):
        """
        مشاهده جزئیات پیام.
        به محض مشاهده، وضعیت پیام به 'خوانده شده' تغییر می‌کند.
        """
        instance = self.get_object()
        
        # لاجیک Seen شدن پیام
        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ===== 3. REPLY ACTION (POST /:id/reply) ===== #
    @extend_schema(
        summary="پاسخ به پیام",
        description="ارسال پاسخ ادمین به ایمیل کاربر و ذخیره آن در سیستم.",
        request=ReplyMessageSerializer,
        responses={200: ContactUsSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reply')
    def reply(self, request, pk=None):
        input_serializer = ReplyMessageSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        reply_txt = input_serializer.validated_data['reply_text']

        try:
            updated_instance = self.service.reply_to_user_message(
                message_id=pk, 
                reply_text=reply_txt,
                admin_user=request.user 
            )
            
            output_serializer = self.get_serializer(updated_instance)
            return Response(output_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ===== 4. DELETE (DELETE /:id) ===== #
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# ===== ویو مدیریت مودال‌ها (Dashboard & Public) ===== #
@extend_schema(tags=['Dashboard-Modal'])
class PromotionalModalViewSet(viewsets.ModelViewSet):
    """
    مدیریت کامل مودال‌ها.
    - ادمین: دسترسی کامل (CRUD).
    - عمومی: فقط دسترسی به دریافت مودال فعال.
    """
    queryset = PromotionalModal.objects.all()
    serializer_class = PromotionalModalSerializer
    
    def get_permissions(self):
        if self.action == 'get_active':
            return [AllowAny()]
        return [IsAdminUser()]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ModalService()

    # ===== متد اختصاصی Create برای استفاده از Transaction سرویس ===== #
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = self.service.create_modal(serializer.validated_data)
        
        output = self.get_serializer(instance)
        return Response(output.data, status=status.HTTP_201_CREATED)

    # ===== متد اختصاصی Update ===== #
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_instance = self.service.update_modal(instance.id, serializer.validated_data)
        
        output = self.get_serializer(updated_instance)
        return Response(output.data)

    # ===== اکشن عمومی: دریافت مودال فعال ===== #
    @extend_schema(tags=['Show-Modal'], summary="دریافت مودال فعال برای نمایش در سایت")
    @action(detail=False, methods=['get'], url_path='active')
    def get_active(self, request):
        """
        این اندپوینت توسط صفحه اصلی سایت صدا زده می‌شود.
        """
        modal = self.service.modal_repo.get_active_modal()
        
        if not modal:
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        serializer = self.get_serializer(modal)
        return Response(serializer.data)

    # ===== اکشن ادمین: تغییر وضعیت سریع ===== #
    @extend_schema(summary="تغییر وضعیت فعال/غیرفعال")
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        instance = self.service.toggle_modal_status(pk)
        return Response({
            'detail': 'وضعیت تغییر کرد.',
            'is_active': instance.is_active
        })
    