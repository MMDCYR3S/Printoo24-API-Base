from django.apps import AppConfig

class CoreConfig(AppConfig):
    """
    یک اپلیکیشن مشترک بین دو پروژه ما
    کارایی این اپلیکیشن به صورتی است  که مدل های مشترک، لایه های منطقی مشترک و همچنین
    گردش کارهایی که مابین پروژه سمت مشتری و ادمین مشترک هست رو مدیریت میکنه.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'