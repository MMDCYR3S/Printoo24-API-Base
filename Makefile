# ==============================================================================
#  ENVIRONMENT DETECTION (Linux vs Windows/Mac)
# ==============================================================================
# این خط چک می‌کند آیا دستور docker-compose وجود دارد؟ اگر بله، از آن استفاده می‌کند.
# در غیر این صورت (مثلاً در ویندوز)، از دستور docker compose استفاده می‌کند.
# 2>&1 ارورها را مخفی می‌کند تا خروجی تمیز بماند.
DC := $(shell command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo "docker compose")

# فایل‌های داکر کامپوز به ترتیب وابستگی
INFRA_FILE := docker-compose.infra.yml
ADMIN_FILE := docker-compose.admin.yml
CUSTOMER_FILE := docker-compose.customer.yml

# ==============================================================================
#  COMMANDS
# ==============================================================================

# دستور پیش‌فرض (فقط با تایپ make)
all: up

# ----------------- UP -----------------
up:
	@echo "Starting project via helper script..."
	@./init_project.sh

# ----------------- DOWN (DEEP CLEAN) -----------------
down:
	@echo "🔥 executing DEEP CLEAN protocol..."
	
	# 1. Customer Layer
	@echo "🔻 Stopping Customer Layer..."
	@$(DC) -f $(CUSTOMER_FILE) down -v --remove-orphans
	
	# 2. Admin Layer
	@echo "🔻 Stopping Admin Layer..."
	@$(DC) -f $(ADMIN_FILE) down -v --remove-orphans
	
	# 3. Infrastructure Layer
	@echo "🔻 Stopping Infrastructure Layer..."
	@$(DC) -f $(INFRA_FILE) down -v --remove-orphans
	
	# 4. Final Cleanup (Optional but Recommended)
	@echo "🧹 Pruning stopped containers to be sure..."
	@docker container prune -f
	
	@echo "💀 System is down and storage (volumes) are WIPED."

# ----------------- UTILS -----------------
logs-admin:
	@$(DC) -f $(ADMIN_FILE) logs -f

logs-customer:
	@$(DC) -f $(CUSTOMER_FILE) logs -f

logs-db:
	@$(DC) -f $(INFRA_FILE) logs -f db