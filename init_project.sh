#!/bin/bash

# توقف اسکریپت در صورت بروز هرگونه خطا
set -e

echo "🚀 Starting Deployment Process..."

# --------------------------------------
# 1. Infrastructure Layer
# --------------------------------------
echo "🟢 [1/4] Starting Infrastructure (DB & Redis)..."
docker-compose -f docker-compose.infra.yml up -d

# انتظار هوشمند برای بالا آمدن دیتابیس
echo "⏳ Waiting for Database to be ready..."
# این لوپ چک می‌کند که آیا پستگرس آماده کوئری گرفتن هست یا نه
until docker exec $(docker-compose -f docker-compose.infra.yml ps -q db) pg_isready -U postgres; do
  echo "   ... Database not ready yet. Retrying in 2 seconds..."
  sleep 2
done
echo "✅ Database is UP and READY."

# --------------------------------------
# 2. Application Layers
# --------------------------------------
echo "🟢 [2/4] Starting Backend Services..."
docker-compose -f docker-compose.admin.yml up -d
docker-compose -f docker-compose.customer.yml up -d

# --------------------------------------
# 3. Database Operations (Migrations)
# --------------------------------------
echo "🟢 [3/4] Running Migrations..."

# نکته: makemigrations معمولاً در پروداکشن اجرا نمی‌شود، اما اینجا طبق درخواست شما گذاشتم
echo "   -> Making migrations for Admin Site..."
docker-compose -f docker-compose.admin.yml exec -T admin_site python manage.py makemigrations
echo "   -> Migrating Admin Site..."
docker-compose -f docker-compose.admin.yml exec -T admin_site python manage.py migrate

# اگر دیتابیس یکی است، مایگریت کردن در یکی از سرویس‌ها کافی است، مگر اینکه اپ‌ها جدا باشند
# اما محض اطمینان برای customer هم چک می‌کنیم (اگر مدل‌های اختصاصی دارد)
echo "   -> Making migrations for Customer Site..."
docker-compose -f docker-compose.customer.yml exec -T customer_site python manage.py makemigrations
echo "   -> Migrating Customer Site..."
docker-compose -f docker-compose.customer.yml exec -T customer_site python manage.py migrate

# --------------------------------------
# 4. Superuser Creation (Idempotent)
# --------------------------------------
echo "🟢 [4/4] Creating Superuser (if not exists)..."

# ما از یک اسکریپت پایتون تک‌خطی استفاده می‌کنیم تا چک کند یوزر هست یا نه
# این روش بسیار امن‌تر از دستور createsuperuser است
docker-compose -f docker-compose.admin.yml exec -T admin_site python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
EMAIL = 'admin@admin.com'
USERNAME = 'admin'
PASSWORD = 'admin'

if not User.objects.filter(username=USERNAME).exists():
    print(f'Creating superuser {USERNAME}...')
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print('Superuser created successfully.')
else:
    print('Superuser already exists. Skipping.')
"

echo "🎉 Deployment Finished Successfully!"
echo "   Admin Panel: http://localhost:8010"
echo "   Customer Site: http://localhost:9010"
echo "   Frontend: http://localhost:5173"
