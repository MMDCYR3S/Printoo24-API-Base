# اگر خطا وجود داشت 
 $ErrorActionPreference = "Stop"

# ===== تغییر نوع نوشتار اگر که داکر مشکل داشت ===== #
 $DC_CMD = "docker-compose"
 Invoke-Expression "$DC_CMD version" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ 'docker-compose' not found. Trying 'docker-compose'..." -ForegroundColor Yellow
    $DC_CMD = "docker-compose"
    Invoke-Expression "$DC_CMD --version" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Neither 'docker-compose' nor 'docker-compose' is working." -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Using command: $DC_CMD" -ForegroundColor Gray

# ===== نام پروژه ===== #
$PROJECT_NAME = "printoo"


# ===== فایل‌های مربوطه ===== #
 $INFRA_FILE = "docker-compose.infra.yml"
 $ADMIN_FILE = "docker-compose.admin.yml"
 $CUSTOMER_FILE = "docker-compose.customer.yml"

# ===== شروع پروسه دپلوی ===== #
Write-Host "Starting Deployment Process..." -ForegroundColor Green

# ===== بخش زیر ساخت - Infra Deploy ===== #
Write-Host "[1/4] Starting Infrastructure (DB & Redis)..." -ForegroundColor Cyan
& $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME up -d

Write-Host "Waiting for Database to be ready..." -ForegroundColor Yellow

 $dbContainerId = & $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME ps -q db

# ===== در صورت بالا نیامدن ===== #
if ([string]::IsNullOrWhiteSpace($dbContainerId)) {
    Write-Host "Critical Error: Could not find DB container ID." -ForegroundColor Red
    Write-Host "Showing current container status for debugging:" -ForegroundColor Red
    & $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME ps
    exit 1
}

Write-Host "Found DB Container ID: $dbContainerId" -ForegroundColor DarkGray

# ===== لوپ برای چک کردن آمادگی دیتابیس ===== #
 $ready = $false
 $maxRetries = 30
 $retryCount = 0

while (-not $ready -and $retryCount -lt $maxRetries) {
    $proc = Start-Process -FilePath "docker" -ArgumentList "exec", "$dbContainerId", "pg_isready", "-U", "postgres" -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\pg_out.txt" -RedirectStandardError "$env:TEMP\pg_err.txt"

    if ($proc.ExitCode -eq 0) {
        $ready = $true
    } else {
        Write-Host "   ... Database not ready yet. Retrying in 2 seconds..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 2
        $retryCount++
    }
}

# ===== اگر در نهایت دیتابیس اجرا نشد ===== #
if (-not $ready) {
    Write-Host "❌ Database failed to start after maximum retries." -ForegroundColor Red
    # نمایش لاگ‌های دیتابیس برای عیب‌یابی
    Write-Host "   Showing recent DB logs:" -ForegroundColor Yellow
    & $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME logs --tail=20 db
    exit 1
}


# ===== بخش سرویس بک‌اند ===== #
Write-Host "✅ Database is UP and READY." -ForegroundColor Green

Write-Host "🟢 [2/4] Starting Backend Services..." -ForegroundColor Cyan
& $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME up -d
& $DC_CMD -f $CUSTOMER_FILE -p $PROJECT_NAME up -d

Start-Sleep -Seconds 5

# --------------------------------------
# 3. Database Operations (Migrations)
# --------------------------------------
Write-Host "🟢 [3/4] Running Migrations..." -ForegroundColor Cyan

# Admin Site Migrations
Write-Host "   -> Making migrations for Admin Site..."
& $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME exec -T admin_site python manage.py makemigrations
Write-Host "   -> Migrating Admin Site..."
& $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME exec -T admin_site python manage.py migrate

# Customer Site Migrations
Write-Host "   -> Making migrations for Customer Site..."
& $DC_CMD -f $CUSTOMER_FILE -p $PROJECT_NAME exec -T customer_site python manage.py makemigrations
Write-Host "   -> Migrating Customer Site..."
& $DC_CMD -f $CUSTOMER_FILE -p $PROJECT_NAME exec -T customer_site python manage.py migrate

# --------------------------------------
# 4. Superuser Creation (Idempotent)
# --------------------------------------
Write-Host "🟢 [4/4] Creating Superuser (if not exists)..." -ForegroundColor Cyan

# کد پایتون
 $pythonScript = @"
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
"@

# اجرای اسکریپت پایتون
& $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME exec -T admin_site python manage.py shell -c $pythonScript

Write-Host "🎉 Deployment Finished Successfully!" -ForegroundColor Green
Write-Host "   Admin Panel: http://localhost:8010" -ForegroundColor White
Write-Host "   Customer Site: http://localhost:9010" -ForegroundColor White
Write-Host "   Frontend: http://localhost" -ForegroundColor White
