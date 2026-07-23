import os
import io
import glob
import logging
import tempfile
from pathlib import Path

from celery import shared_task
from PIL import Image as PILImage

from django.conf import settings
from django.core.files.base import ContentFile

from core.models import ProductImage

logger = logging.getLogger('product.tasks')

# ──────────────────────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────────────────────

# کیفیت پیش‌فرض فشرده‌سازی - در settings هم می‌تونی override کنی
IMAGE_QUALITY = getattr(settings, 'PRODUCT_IMAGE_COMPRESS_QUALITY', 80)
# حداکثر بُعد (عرض یا ارتفاع) بعد از resize
IMAGE_MAX_DIM = getattr(settings, 'PRODUCT_IMAGE_MAX_DIM', 512)


def _compress_image_bytes(source_path: str) -> tuple[bytes, str]:
    """
    یک فایل تصویری رو باز می‌کنه، در صورت نیاز resize می‌کنه،
    و byte های فشرده‌شده به همراه پسوند مناسب رو برمی‌گردونه.

    خروجی: (compressed_bytes, extension)  → e.g. (b'...', '.webp')
    استثنا: اگر فایل خراب باشه یا PIL نتونه بازش کنه.
    """
    with PILImage.open(source_path) as img:
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGBA')
            fmt = 'WEBP'
            ext = '.webp'
        else:
            img = img.convert('RGB')
            fmt = 'WEBP'
            ext = '.webp'

        w, h = img.size
        if max(w, h) > IMAGE_MAX_DIM:
            ratio = IMAGE_MAX_DIM / max(w, h)
            img = img.resize(
                (int(w * ratio), int(h * ratio)),
                PILImage.LANCZOS
            )

        buffer = io.BytesIO()
        img.save(buffer, format=fmt, quality=IMAGE_QUALITY, method=6)
        return buffer.getvalue(), ext


# ──────────────────────────────────────────────────────────────
#  Task 1 - فشرده‌سازی عکس تازه آپلود شده
# ──────────────────────────────────────────────────────────────

@shared_task(
    name='compress_new_product_image_task',
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,          # پیام فقط بعد از موفقیت تأیید بشه
)
def compress_new_product_image_task(self, product_image_id: int):
    """
    Task 1 - عکس تازه آپلود‌شده رو فشرده می‌کنه.

    فرایند ایمن:
    1. فایل اصلی دست نخورده می‌مونه تا زمانی که فشرده‌سازی کامل بشه.
    2. فایل فشرده در یک مسیر موقت ذخیره می‌شه.
    3. فقط بعد از موفقیت کامل، فایل جدید روی مدل ست می‌شه.
    4. فایل قدیمی حذف می‌شه.
    اگر هر مرحله‌ای fail بشه، فایل اصلی سالم باقی می‌مونه.
    """
    logger.info(f"[Compress New] Starting → ProductImage #{product_image_id}")

    try:
        instance = ProductImage.objects.get(id=product_image_id)
    except ProductImage.DoesNotExist:
        logger.error(f"[Compress New] ProductImage #{product_image_id} not found. Aborting.")
        return f"ProductImage #{product_image_id} not found"

    # ── بررسی اینکه فایل واقعاً وجود داره ──
    original_file_field = instance.image
    if not original_file_field or not original_file_field.name:
        logger.warning(f"[Compress New] No image file on ProductImage #{product_image_id}. Skipping.")
        return "No image file"

    # مسیر فیزیکی روی دیسک
    try:
        original_abs_path = original_file_field.path  # MEDIA_ROOT + name
    except Exception:
        logger.error(f"[Compress New] Cannot resolve path for ProductImage #{product_image_id}.")
        return "Cannot resolve path"

    if not os.path.exists(original_abs_path):
        logger.error(f"[Compress New] File missing on disk: {original_abs_path}")
        return "File missing on disk"

    # ── فشرده‌سازی در یک فایل موقت ──
    tmp_path = None
    try:
        compressed_bytes, ext = _compress_image_bytes(original_abs_path)

        # اسم جدید با همون stem اما پسوند webp
        original_stem = Path(original_file_field.name).stem
        new_filename = f"{original_stem}_c{ext}"  # _c = compressed

        # ذخیره‌ی موقت برای اطمینان قبل از جایگزینی
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext, dir=settings.MEDIA_ROOT)
        with os.fdopen(tmp_fd, 'wb') as tmp_file:
            tmp_file.write(compressed_bytes)

        # ── جایگزینی ایمن: اول ذخیره جدید، بعد حذف قدیمی ──
        old_name = original_file_field.name

        instance.image.save(
            new_filename,
            ContentFile(compressed_bytes),
            save=True   # instance.save() هم صدا زده می‌شه
        )

        # حذف فایل قدیمی فقط اگر متفاوت باشه و وجود داشته باشه
        if old_name and old_name != instance.image.name:
            old_abs = os.path.join(settings.MEDIA_ROOT, old_name)
            if os.path.exists(old_abs):
                os.remove(old_abs)
                logger.info(f"[Compress New] Removed old file: {old_abs}")

        logger.info(
            f"[Compress New] Done → ProductImage #{product_image_id} | "
            f"size: {len(compressed_bytes) // 1024} KB"
        )
        return f"Compressed: ProductImage #{product_image_id}"

    except Exception as exc:
        logger.error(f"[Compress New] Error on #{product_image_id}: {exc}", exc_info=True)
        raise self.retry(exc=exc)

    finally:
        # فایل موقت رو حتماً پاک کن
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# ──────────────────────────────────────────────────────────────
#  Task 2 - فشرده‌سازی دسته‌ای عکس‌های قدیمی (bulk / backfill)
# ──────────────────────────────────────────────────────────────
@shared_task(
    name='compress_existing_product_images_task',
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def compress_existing_product_images_task(self, batch_size: int = 50, offset: int = 0):
    logger.info(f"[Compress Bulk] Starting batch | offset={offset}, size={batch_size}")

    from core.models import ProductCategory
    from django.db.models import Q

    product_image_success = 0
    product_image_fail = 0
    category_success = 0
    category_fail = 0

    # ===== بخش ۱: ProductImage ===== #
    qs = (
        ProductImage.objects
        .exclude(image='')
        .exclude(image__endswith='_c.webp')
        .order_by('id')[offset: offset + batch_size]
    )
    ids = list(qs.values_list('id', flat=True))
    logger.info(f"[Compress Bulk] Found {len(ids)} ProductImage(s) to compress.")

    for img_id in ids:
        try:
            instance = ProductImage.objects.get(id=img_id)
            original_abs_path = instance.image.path

            if not os.path.exists(original_abs_path):
                logger.warning(f"[Compress Bulk] File missing for ProductImage #{img_id}: {original_abs_path}")
                product_image_fail += 1
                continue

            compressed_bytes, ext = _compress_image_bytes(original_abs_path)
            original_stem = Path(instance.image.name).stem
            new_filename = f"{original_stem}_c{ext}"
            old_name = instance.image.name

            instance.image.save(new_filename, ContentFile(compressed_bytes), save=True)

            if old_name and old_name != instance.image.name:
                old_abs = os.path.join(settings.MEDIA_ROOT, old_name)
                if os.path.exists(old_abs):
                    os.remove(old_abs)

            product_image_success += 1
            logger.info(f"[Compress Bulk] ✓ ProductImage #{img_id}")

        except ProductImage.DoesNotExist:
            logger.warning(f"[Compress Bulk] ProductImage #{img_id} deleted mid-task, skipping.")
            product_image_fail += 1
        except Exception as e:
            logger.error(f"[Compress Bulk] ✗ ProductImage #{img_id}: {e}", exc_info=True)
            product_image_fail += 1

    # ===== بخش ۲: ProductCategory ===== #
    # فیلتر درست: حداقل یکی از دو فیلد مقدار داره و _c.webp نیست
    cat_qs = (
        ProductCategory.objects
        .filter(
            Q(banner_wide__gt='') | Q(banner_box__gt='')  # خالی نیست
        )
        .exclude(
            Q(banner_wide__endswith='_c.webp') & Q(banner_box__endswith='_c.webp')  # هر دو compress شدن
        )
        .order_by('id')[offset: offset + batch_size]
    )
    cat_ids = list(cat_qs.values_list('id', flat=True))
    logger.info(f"[Compress Bulk] Found {len(cat_ids)} ProductCategory(s) to compress.")

    for cat_id in cat_ids:
        try:
            cat = ProductCategory.objects.get(id=cat_id)
            cat_changed = False

            for field_name in ['banner_wide', 'banner_box']:
                field = getattr(cat, field_name)

                # ===== بررسی خالی بودن ===== #
                if not field or not field.name or field.name == '':
                    logger.debug(f"[Compress Bulk] Category #{cat_id} field={field_name} is empty, skipping.")
                    continue

                # ===== بررسی compress شده بودن ===== #
                if field.name.endswith('_c.webp'):
                    logger.debug(f"[Compress Bulk] Category #{cat_id} field={field_name} already compressed, skipping.")
                    continue

                try:
                    abs_path = field.path
                except Exception:
                    logger.warning(f"[Compress Bulk] Cannot resolve path for Category #{cat_id} field={field_name}")
                    continue

                if not os.path.exists(abs_path):
                    logger.warning(f"[Compress Bulk] File missing: {abs_path}")
                    continue

                logger.info(f"[Compress Bulk] Compressing Category #{cat_id} field={field_name}: {abs_path}")

                compressed_bytes, ext = _compress_image_bytes(abs_path)
                old_name = field.name
                stem = Path(old_name).stem
                new_filename = f"{stem}_c{ext}"

                # ===== ذخیره فایل جدید ===== #
                getattr(cat, field_name).save(
                    new_filename,
                    ContentFile(compressed_bytes),
                    save=False
                )
                cat_changed = True

                # ===== حذف فایل قدیمی ===== #
                new_name = getattr(cat, field_name).name
                if old_name and old_name != new_name:
                    old_abs = os.path.join(settings.MEDIA_ROOT, old_name)
                    if os.path.exists(old_abs):
                        os.remove(old_abs)
                        logger.info(f"[Compress Bulk] Removed old file: {old_abs}")

            if cat_changed:
                cat.save(update_fields=['banner_wide', 'banner_box'])
                category_success += 1
                logger.info(f"[Compress Bulk] ✓ ProductCategory #{cat_id}")
            else:
                logger.info(f"[Compress Bulk] ProductCategory #{cat_id} - nothing to compress.")

        except ProductCategory.DoesNotExist:
            logger.warning(f"[Compress Bulk] ProductCategory #{cat_id} deleted mid-task, skipping.")
            category_fail += 1
        except Exception as e:
            logger.error(f"[Compress Bulk] ✗ ProductCategory #{cat_id}: {e}", exc_info=True)
            category_fail += 1

    logger.info(
        f"[Compress Bulk] Batch done | "
        f"products: success={product_image_success}, failed={product_image_fail} | "
        f"categories: success={category_success}, failed={category_fail}"
    )

    # ===== batch بعدی در صورت نیاز ===== #
    if len(ids) == batch_size or len(cat_ids) == batch_size:
        next_offset = offset + batch_size
        logger.info(f"[Compress Bulk] Scheduling next batch | offset={next_offset}")
        compress_existing_product_images_task.apply_async(
            kwargs={'batch_size': batch_size, 'offset': next_offset},
            countdown=5
        )

    return (
        f"Batch done | "
        f"products: success={product_image_success}, failed={product_image_fail} | "
        f"categories: success={category_success}, failed={category_fail}"
    )


# ──────────────────────────────────────────────────────────────
#  Task جدید - فشرده‌سازی عکس‌های category هنگام ایجاد/ویرایش
# ──────────────────────────────────────────────────────────────

@shared_task(
    name='compress_category_images_task',
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def compress_category_images_task(self, category_id: int):
    """
    بعد از ایجاد یا ویرایش category، banner_wide و banner_box رو فشرده می‌کنه.
    """
    logger.info(f"[Compress Category] Starting → ProductCategory #{category_id}")

    from core.models import ProductCategory

    try:
        cat = ProductCategory.objects.get(id=category_id)
    except ProductCategory.DoesNotExist:
        logger.error(f"[Compress Category] ProductCategory #{category_id} not found.")
        return f"ProductCategory #{category_id} not found"

    changed_fields = []

    for field_name in ['banner_wide', 'banner_box']:
        field = getattr(cat, field_name)
        if not field or not field.name:
            continue
        if field.name.endswith('_c.webp'):
            continue  # قبلاً compress شده

        try:
            abs_path = field.path
        except Exception:
            logger.error(f"[Compress Category] Cannot resolve path for field={field_name} on #{category_id}")
            continue

        if not os.path.exists(abs_path):
            logger.error(f"[Compress Category] File missing: {abs_path}")
            continue

        tmp_path = None
        try:
            compressed_bytes, ext = _compress_image_bytes(abs_path)
            stem = Path(field.name).stem
            new_filename = f"{stem}_c{ext}"
            old_name = field.name

            # ذخیره موقت برای اطمینان
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext, dir=settings.MEDIA_ROOT)
            with os.fdopen(tmp_fd, 'wb') as tmp_file:
                tmp_file.write(compressed_bytes)

            # جایگزینی ایمن
            field.save(new_filename, ContentFile(compressed_bytes), save=False)
            changed_fields.append(field_name)

            if old_name and old_name != getattr(cat, field_name).name:
                old_abs = os.path.join(settings.MEDIA_ROOT, old_name)
                if os.path.exists(old_abs):
                    os.remove(old_abs)
                    logger.info(f"[Compress Category] Removed old file: {old_abs}")

            logger.info(f"[Compress Category] ✓ field={field_name} on #{category_id}")

        except Exception as exc:
            logger.error(f"[Compress Category] ✗ field={field_name} on #{category_id}: {exc}", exc_info=True)
            raise self.retry(exc=exc)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    if changed_fields:
        cat.save(update_fields=changed_fields)
        logger.info(f"[Compress Category] Done → #{category_id} | fields: {changed_fields}")

    return f"Compressed: ProductCategory #{category_id} | fields: {changed_fields}"


# ──────────────────────────────────────────────────────────────
#  Task 3 - پاک‌سازی فایل‌های temp_ در پوشه media
# ──────────────────────────────────────────────────────────────

@shared_task(
    name='cleanup_temp_media_files_task',
    bind=True,
    max_retries=1,
)
def cleanup_temp_media_files_task(self, max_age_seconds: int = 3600):
    """
    Task 3 - پوشه‌های media رو اسکن می‌کنه و فایل‌هایی که:
      - اسمشون با temp_ شروع می‌شه
      - قدیمی‌تر از max_age_seconds ثانیه هستند (پیش‌فرض: ۱ ساعت)
    رو حذف می‌کنه.

    ایمنی: فایل‌های جدیدتر از max_age_seconds دست نخورده می‌مونن،
    چون ممکنه هنوز توسط یک task دیگه‌ای در حال پردازش باشن.

    پیشنهاد: هر شب یک بار با Celery Beat اجرا بشه:
        # در settings.py یا celery.py:
        app.conf.beat_schedule = {
            'cleanup-temp-media-nightly': {
                'task': 'cleanup_temp_media_files_task',
                'schedule': crontab(hour=3, minute=0),  # ۳ بامداد
            },
        }
    """
    import time

    media_root = settings.MEDIA_ROOT
    now = time.time()
    removed_count = 0
    error_count = 0

    logger.info(f"[Cleanup Temp] Scanning MEDIA_ROOT: {media_root} | max_age={max_age_seconds}s")

    # جستجوی بازگشتی در تمام زیرپوشه‌های media
    pattern = os.path.join(media_root, '**', 'temp_*')
    temp_files = glob.glob(pattern, recursive=True)

    if not temp_files:
        logger.info("[Cleanup Temp] No temp_ files found.")
        return "No temp files found"

    logger.info(f"[Cleanup Temp] Found {len(temp_files)} temp_ file(s). Checking age...")

    for file_path in temp_files:
        try:
            if not os.path.isfile(file_path):
                continue  # اگر directory بود رد کن

            file_age = now - os.path.getmtime(file_path)

            if file_age < max_age_seconds:
                logger.debug(
                    f"[Cleanup Temp] Skipping (too new, {int(file_age)}s old): {file_path}"
                )
                continue

            os.remove(file_path)
            removed_count += 1
            logger.info(f"[Cleanup Temp] Removed ({int(file_age)}s old): {file_path}")

        except OSError as e:
            error_count += 1
            logger.error(f"[Cleanup Temp] Failed to remove {file_path}: {e}")

    # پاک‌سازی پوشه‌های خالی که بعد از حذف فایل‌ها موندن
    _remove_empty_dirs(media_root)

    logger.info(
        f"[Cleanup Temp] Done | removed={removed_count}, errors={error_count}"
    )
    return f"Cleanup done: removed={removed_count}, errors={error_count}"


def _remove_empty_dirs(root: str):
    """پوشه‌های خالی (به جز root) رو حذف می‌کنه."""
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if dirpath == root:
            continue
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
                logger.debug(f"[Cleanup Temp] Removed empty dir: {dirpath}")
            except OSError:
                pass