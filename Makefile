# Makefile - Orders Serverless API

.PHONY: help init plan apply destroy logs clean test format validate

# Variables
ENV ?= dev
REGION ?= eu-west-1

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## Inicializar Terraform
	@echo "🔧 Inicializando Terraform..."
	cd infra && terraform init

plan: ## Planificar cambios de infraestructura
	@echo "📋 Planificando deployment para $(ENV)..."
	cd infra && terraform plan -var-file=environments/$(ENV).tfvars

apply: ## Aplicar cambios de infraestructura
	@echo "🚀 Desplegando infraestructura en $(ENV)..."
	cd infra && terraform apply -var-file=environments/$(ENV).tfvars

deploy: apply ## Alias para apply

destroy: ## Destruir toda la infraestructura
	@echo "🗑️  Destruyendo infraestructura en $(ENV)..."
	@echo "⚠️  ¿Estás seguro? [y/N] " && read ans && [ $${ans:-N} = y ]
	cd infra && terraform destroy -var-file=environments/$(ENV).tfvars

output: ## Mostrar outputs de Terraform
	@cd infra && terraform output

logs-lambda: ## Ver logs de Lambda
	@echo "📊 Mostrando logs de Lambda..."
	@API_NAME=$$(cd infra && terraform output -raw lambda_function_name); \
	aws logs tail /aws/lambda/$$API_NAME --follow --region $(REGION)

logs-api: ## Ver logs de API Gateway
	@echo "📊 Mostrando logs de API Gateway..."
	@API_NAME=$$(cd infra && terraform output -raw api_gateway_id); \
	aws logs tail /aws/apigateway/orders-api-$(ENV) --follow --region $(REGION)

create-user: ## Crear usuario de prueba en Cognito
	@echo "👤 Creando usuario de prueba..."
	@read -p "Email: " EMAIL; \
	read -sp "Password: " PASSWORD; \
	echo ""; \
	USER_POOL_ID=$$(cd infra && terraform output -raw cognito_user_pool_id); \
	aws cognito-idp admin-create-user \
		--user-pool-id $$USER_POOL_ID \
		--username $$EMAIL \
		--user-attributes Name=email,Value=$$EMAIL \
		--temporary-password TempPass123! \
		--message-action SUPPRESS \
		--region $(REGION); \
	aws cognito-idp admin-set-user-password \
		--user-pool-id $$USER_POOL_ID \
		--username $$EMAIL \
		--password $$PASSWORD \
		--permanent \
		--region $(REGION)

get-token: ## Obtener JWT token
	@echo "🔐 Obteniendo token JWT..."
	@read -p "Email: " EMAIL; \
	read -sp "Password: " PASSWORD; \
	echo ""; \
	CLIENT_ID=$$(cd infra && terraform output -raw cognito_user_pool_client_id); \
	aws cognito-idp initiate-auth \
		--auth-flow USER_PASSWORD_AUTH \
		--client-id $$CLIENT_ID \
		--auth-parameters USERNAME=$$EMAIL,PASSWORD=$$PASSWORD \
		--region $(REGION) \
		--query 'AuthenticationResult.IdToken' \
		--output text

test-api: ## Test rápido de la API
	@echo "🧪 Testing API..."
	@API_URL=$$(cd infra && terraform output -raw api_gateway_url); \
	read -p "Token JWT: " TOKEN; \
	echo ""; \
	echo "Creating order..."; \
	curl -X POST $$API_URL/v1/orders \
		-H "Authorization: Bearer $$TOKEN" \
		-H "Content-Type: application/json" \
		-d '{"customer_id":"test-001","total_amount":99.99,"status":"PENDING","items":[]}' | jq

format: ## Formatear código Python
	@echo "🎨 Formateando código..."
	black src/orders/*.py
	isort src/orders/*.py

lint: ## Linter para Python
	@echo "🔍 Ejecutando linter..."
	pylint src/orders/*.py

validate: ## Validar configuración de Terraform
	@echo "✅ Validando Terraform..."
	cd infra && terraform fmt -check
	cd infra && terraform validate

format-tf: ## Formatear archivos Terraform
	@echo "🎨 Formateando Terraform..."
	cd infra && terraform fmt -recursive

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf infra/.terraform.lock.hcl
	rm -rf infra/lambda_function.zip
	@echo "✅ Limpieza completada"

cost: ## Estimar costes con infracost (requiere infracost CLI)
	@echo "💰 Estimando costes..."
	cd infra && infracost breakdown --path .

security: ## Análisis de seguridad con checkov
	@echo "🔒 Analizando seguridad..."
	checkov -d infra/

info: ## Mostrar información del deployment
	@echo "📌 Información del deployment ($(ENV)):"
	@echo ""
	@cd infra && terraform output

all: init plan apply info ## Deployment completo

dev: ## Deploy rápido a dev
	@$(MAKE) ENV=dev apply

prod: ## Deploy a producción (con confirmación)
	@echo "⚠️  ¡Vas a deployar a PRODUCCIÓN!"
	@echo "¿Estás seguro? [y/N] " && read ans && [ $${ans:-N} = y ]
	@$(MAKE) ENV=prod apply

.DEFAULT_GOAL := help
