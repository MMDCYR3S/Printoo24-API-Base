# این دستور پیش‌فرض است
all: up

up:
	@echo "Starting project via helper script..."
	@./init_project.sh

down:
	@echo "Stopping all services..."
	@docker-compose -f docker-compose.customer.yml down
	@docker-compose -f docker-compose.admin.yml down
	@docker-compose -f docker-compose.infra.yml down

logs:
	@docker-compose -f docker-compose.admin.yml logs -f

clean: down
	@echo "Cleaning up volumes (Danger Zone)..."
	@docker volume rm printoo24_postgres_data || true
