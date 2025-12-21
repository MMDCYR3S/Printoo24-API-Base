from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from core.order.models import Order, OrderPrintReport, OrderPrintItem, OrderPrintAttachment
from core.models import User
from core.domain.infrastructure.logger import AuditLogDomainService

# ========== PRINT SERVICE ========== #
class PrintMaterialService:
    """
    سرویس مدیریت مصرف متریال در واحد چاپ.
    """
    def __init__(self):
        self.audit_service = AuditLogDomainService()

    @transaction.atomic
    def register_usage_report(self, 
                              order: Order, 
                              user: User, 
                              title: str, 
                              description: str, 
                              items_data: List[Dict[str, Any]], 
                              attachments_list: List[Any] = None) -> OrderPrintReport:
        """
        ثبت گزارش مصرف متریال برای یک سفارش.
        """
        # ===== اعتبارسنجی ورودی ===== #
        if not items_data:
            raise ValidationError("لیست اقلام مصرفی نمی‌تواند خالی باشد.")

        # ===== اجرای عملیات (ایجاد هدر) ===== #
        report = OrderPrintReport.objects.create(
            order=order,
            created_by=user,
            title=title,
            description=description
        )

        # ===== ایجاد اقلام مصرف ===== #
        items_to_create = []
        for item in items_data:
            items_to_create.append(OrderPrintItem(
                report=report,
                material_type=item['material_type'],
                custom_title=item.get('custom_title', ''),
                price=item['price'],
                description=item.get('description', '')
            ))
        
        # ===== ثبت اقلام گروهی ===== #
        OrderPrintItem.objects.bulk_create_items(items_to_create)

        # ===== ثبت پیوست ها ===== #
        if attachments_list:
            attachments_to_create = []
            for file in attachments_list:
                attachments_to_create.append(OrderPrintAttachment(
                    report=report,
                    file=file,
                    title=file.name
                ))
            OrderPrintAttachment.objects.bulk_create_attachments(attachments_to_create)

        # ===== ثبت لاگ ===== #
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='CREATE_PRINT_REPORT',
            changes={
                'report_id': report.id,
                'title': title,
                'items_count': len(items_data),
                'total_price': sum(float(i['price']) for i in items_data)
            },
            description=_(f"ثبت گزارش مصرف چاپ: {title}")
        )

        return report

    @transaction.atomic
    def update_print_report(self, 
                            report_id: int, 
                            user: User, 
                            data: Dict[str, Any], 
                            new_attachments: List[Any] = None) -> OrderPrintReport:
        """
        ویرایش کامل یک گزارش مصرف (شامل هدر و اقلام).
        """
        # ===== اعتبارسنجی ورودی ===== #
        report = OrderPrintReport.objects.get_by_id(report_id)
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        # ===== ویرایش هدر ===== #
        if 'title' in data: report.title = data['title']
        if 'description' in data: report.description = data['description']
        report.save()

        # ===== ویرایش اقلام (Logic Preservation) ===== #
        changes_log = {'report_id': report_id}
        if 'items' in data:
            changes_log['items_modified'] = True
            changes_log['new_items_count'] = len(data['items'])

        if 'items' in data:
            incoming_items = data['items']
            
            new_items_data = [i for i in incoming_items if not i.get('id')]
            existing_items_map = {i['id']: i for i in incoming_items if i.get('id')}
            
            # ===== مجموع آیتم هایی که در پایگاه داده وجود دارد ===== #
            current_db_items = report.items.all()
            current_db_ids = set(item.id for item in current_db_items)
            incoming_ids = set(existing_items_map.keys())

            # ===== حذف آیتم های که در پایگاه داده وجود دارد ===== #
            ids_to_delete = current_db_ids - incoming_ids
            if ids_to_delete:
                OrderPrintItem.objects.filter(id__in=ids_to_delete).delete()

            # ===== آپدیت آیتم هایی که در پایگاه داده وجود دارد ===== #
            for item in current_db_items:
                if item.id in existing_items_map:
                    item_data = existing_items_map[item.id]
                    item.material_type = item_data.get('material_type', item.material_type)
                    item.custom_title = item_data.get('custom_title', item.custom_title)
                    item.price = item_data.get('price', item.price)
                    item.description = item_data.get('description', item.description)
                    item.save()

            # ===== افزودن اقلام جدید ===== #
            if new_items_data:
                items_to_create = []
                for item in new_items_data:
                    items_to_create.append(OrderPrintItem(
                        report=report,
                        material_type=item['material_type'],
                        custom_title=item.get('custom_title', ''),
                        price=item['price'],
                        description=item.get('description', '')
                    ))
                OrderPrintItem.objects.bulk_create_items(items_to_create)

        # ===== افزودن فایل های جدید ===== #
        if new_attachments:
            attachments_to_create = []
            for file in new_attachments:
                attachments_to_create.append(OrderPrintAttachment(
                    report=report,
                    file=file,
                    title=file.name
                ))
            OrderPrintAttachment.objects.bulk_create_attachments(attachments_to_create)

        # ===== ثبت لاگ ویرایش ===== #       
        self.audit_service.record_log(
            user=user,
            obj=report.order,
            action='UPDATE_PRINT_REPORT',
            changes=changes_log,
            description=_(f"ویرایش گزارش مصرف چاپ: {report.title}")
        )

        return report

    @transaction.atomic
    def delete_report(self, report_id: int, user: User):
        """ حذف گزارش """
        report = OrderPrintReport.objects.get_by_id(report_id)
        
        if not report:
            raise ValidationError("گزارش یافت نشد.")

        report_title = report.title
        order = report.order
        
        report.delete()
        
        self.audit_service.record_log(
            user=user,
            obj=order,
            action='DELETE_PRINT_REPORT',
            changes={
                'deleted_report_id': report_id,
                'deleted_report_title': report_title
            },
            description=_(f"حذف گزارش مصرف چاپ: {report_title}")
        )
