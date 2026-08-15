# Generated manually: add Quotation.cart_item (OneToOne) to link a proforma
# to a CartItem before it is converted into an Order.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_cart_session_key_alter_cart_user_and_more'),
        ('core', '0029_alter_payment_method_financiallog'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotation',
            name='cart_item',
            field=models.OneToOneField(blank=True, help_text='تا زمانی که آیتم سبد خرید به سفارش تبدیل نشده، پیش‌فاکتور به اینجا متصل است. پس از تبدیل، این اتصال حذف و به سفارش گره می‌خورد.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotation', to='cart.cartitem', verbose_name='آیتم سبد خرید'),
        ),
    ]