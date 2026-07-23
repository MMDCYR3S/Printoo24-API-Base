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
until docker exec $(docker-compose -f docker-compose.infra.yml ps -q db) pg_isready -U postgres; do
  echo "   ... Database not ready yet. Retrying in 2 seconds..."
  sleep 2
done
echo "✅ Database is UP and READY."

# --------------------------------------
# 2. Application Layers
# --------------------------------------
echo "🟢 [2/4] Starting Backend Services..."
docker-compose -f docker-compose.yml up -d

# --------------------------------------
# 3. Database Operations (Migrations)
# --------------------------------------
echo "🟢 [3/4] Running Migrations..."
echo "   -> Running migrations..."
docker-compose -f docker-compose.yml exec -T backend python manage.py migrate

# --------------------------------------
# 4. Superuser Creation (Idempotent)
# --------------------------------------
echo "🟢 [4/4] Creating Superuser (if not exists)..."
docker-compose -f docker-compose.yml exec -T backend python manage.py shell -c "
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
echo "   Backend: http://localhost:9010"
echo "   Frontend: http://localhost:5173"