param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("up", "down", "logs-admin", "logs-customer", "logs-db", "help")]
    [string]$Command
)

# تشخیص دستور داکر (مشابه اسکریپت بالا)
 $DC_CMD = "docker-compose"
Invoke-Expression "$DC_CMD version" | Out-Null
if ($LASTEXITCODE -ne 0) {
    $DC_CMD = "docker-compose"
}

# نام پروژه باید با اسکریپت init_project یکی باشد
 $PROJECT_NAME = "printoo"

# تعریف فایل‌ها
 $INFRA_FILE = "docker-compose.infra.yml"
 $ADMIN_FILE = "docker-compose.admin.yml"
 $CUSTOMER_FILE = "docker-compose.customer.yml"

switch ($Command) {
    "up" {
        Write-Host "Starting project via helper script..."
        & .\init_project.ps1
    }
    "down" {
        Write-Host "🔥 executing DEEP CLEAN protocol..." -ForegroundColor Red
        
        # اضافه کردن -p $PROJECT_NAME به همه دستورات
        Write-Host "🔻 Stopping Customer Layer..."
        & $DC_CMD -f $CUSTOMER_FILE -p $PROJECT_NAME down -v --remove-orphans
        
        Write-Host "🔻 Stopping Admin Layer..."
        & $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME down -v --remove-orphans
        
        Write-Host "🔻 Stopping Infrastructure Layer..."
        & $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME down -v --remove-orphans
        
        Write-Host "🧹 Pruning stopped containers..."
        docker container prune -f
        
        Write-Host "💀 System is down and storage (volumes) are WIPED." -ForegroundColor DarkRed
    }
    "logs-admin" {
        & $DC_CMD -f $ADMIN_FILE -p $PROJECT_NAME logs -f
    }
    "logs-customer" {
        & $DC_CMD -f $CUSTOMER_FILE -p $PROJECT_NAME logs -f
    }
    "logs-db" {
        & $DC_CMD -f $INFRA_FILE -p $PROJECT_NAME logs -f db
    }
    "help" {
        Write-Host "Available commands:"
        Write-Host "  .\Make.ps1 up          : Start the whole project"
        Write-Host "  .\Make.ps1 down        : Stop and remove everything (Deep Clean)"
        Write-Host "  .\Make.ps1 logs-admin  : View Admin logs"
        Write-Host "  .\Make.ps1 logs-customer : View Customer logs"
        Write-Host "  .\Make.ps1 logs-db     : View Database logs"
    }
}