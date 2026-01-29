# 📦 Orders API - Serverless Architecture

> API REST serverless para gestión de pedidos, construida con arquitectura moderna en AWS.

[![Terraform](https://img.shields.io/badge/Terraform-1.0+-purple.svg)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Serverless-orange.svg)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-36%20passing-brightgreen.svg)](docs/TESTING.md)
[![Coverage](https://img.shields.io/badge/Coverage-73.57%25-yellow.svg)](docs/PHASE2_SUMMARY.md)

**Stack:** Lambda | API Gateway | DynamoDB | Cognito | CloudWatch | Terraform

**⚡ Quick Links:**
- [🚀 Quick Start (5 min)](docs/QUICKSTART.md)
- [💻 Windows Guide](docs/WINDOWS_GUIDE.md)
- [🧪 Testing Guide](docs/TESTING.md) ⭐ NEW
- [🎯 Executive Summary](docs/EXECUTIVE_SUMMARY.md)
- [📖 API Examples](docs/API_EXAMPLES.md)
- [🏗️ Architecture Details](docs/architecture.md)
- [📋 Decisiones Técnicas](docs/decisions.md)
- [✅ Verification Checklist](docs/VERIFICATION_CHECKLIST.md)
- [📂 Project Structure](docs/PROJECT_STRUCTURE.md)
- [🎉 Project Completion Summary](PROJECT_COMPLETION.md)

---

## 🏗️ Arquitectura

```
Client (HTTPS + JWT)
    ↓
API Gateway (REST API)
    ↓
Cognito Authorizer
    ↓
Lambda Function (Python 3.11)
    ↓
DynamoDB
```

### Componentes

- **API Gateway**: REST API con rate limiting y usage plans
- **Lambda**: Python 3.11 con arquitectura limpia (handler → repository → DynamoDB)
- **DynamoDB**: Base de datos NoSQL con GSI para consultas por cliente
- **Cognito**: Autenticación JWT con User Pool
- **CloudWatch**: Logs y métricas centralizadas
- **Terraform**: Infraestructura como código

## 📋 Recursos y Endpoints

### Order Model

```json
{
  "order_id": "uuid",
  "customer_id": "string",
  "status": "PENDING|PROCESSING|COMPLETED|CANCELLED",
  "total_amount": "decimal",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "items": []
}
```

### API Endpoints

| Method | Path | Descripción |
|--------|------|-------------|
| `POST` | `/v1/orders` | Crear un pedido |
| `GET` | `/v1/orders` | Listar pedidos |
| `GET` | `/v1/orders/{id}` | Obtener un pedido |
| `PUT` | `/v1/orders/{id}` | Actualizar un pedido |
| `DELETE` | `/v1/orders/{id}` | Eliminar un pedido |

Todos los endpoints requieren autenticación JWT (Cognito).

## 🚀 Deployment

### Requisitos

- AWS CLI configurado
- Terraform >= 1.0
- Python 3.11
- Cuenta AWS con permisos apropiados

### Desplegar infraestructura

```bash
# Inicializar Terraform
cd infra
terraform init

# Revisar plan de deployment
terraform plan -var-file=environments/dev.tfvars

# Aplicar cambios
terraform apply -var-file=environments/dev.tfvars

# Ver outputs (URL de API, etc.)
terraform output
```

### Desplegar a Producción

```bash
terraform apply -var-file=environments/prod.tfvars
```

### Outputs importantes

Terraform te dará:
- `api_gateway_url`: URL base de la API
- `cognito_user_pool_id`: ID del User Pool para autenticación
- `cognito_user_pool_client_id`: Client ID para la aplicación

## 🧪 Testing

El proyecto incluye una suite completa de tests con **36 tests unitarios** (100% passing) y **73.57% de cobertura de código**.

### Ejecutar tests

```bash
# Instalar dependencias de testing
pip install -r tests/requirements.txt

# Ejecutar todos los tests
pytest tests/unit/ -v

# Ejecutar con cobertura
pytest tests/unit/ --cov=src/orders --cov-report=term-missing

# Ejecutar tests específicos
pytest tests/unit/test_handler.py -v
pytest tests/unit/test_models.py -v
pytest tests/unit/test_repository.py -v
```

### Suite de tests

- **14 tests de handler**: POST, GET, PUT, DELETE, error handling
- **13 tests de models**: Order, OrderItem, OrderStatus, validaciones
- **9 tests de repository**: CRUD operations con DynamoDB (moto)

### CI/CD

GitHub Actions ejecuta automáticamente:
- Tests unitarios en Python 3.11
- Reporte de cobertura
- Pre-commit hooks (black, flake8, isort, bandit)

📖 **Documentación completa**: [TESTING.md](docs/TESTING.md) | [PHASE2_SUMMARY.md](docs/PHASE2_SUMMARY.md)

## 🔐 Autenticación

La API usa Cognito con JWT tokens.

### Crear un usuario

```bash
aws cognito-idp sign-up \
  --client-id <COGNITO_CLIENT_ID> \
  --username usuario@example.com \
  --password TuPassword123! \
  --user-attributes Name=email,Value=usuario@example.com
```

### Confirmar usuario (admin)

```bash
aws cognito-idp admin-confirm-sign-up \
  --user-pool-id <USER_POOL_ID> \
  --username usuario@example.com
```

### Obtener token

```bash
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id <COGNITO_CLIENT_ID> \
  --auth-parameters USERNAME=usuario@example.com,PASSWORD=TuPassword123!
```

### Usar la API

```bash
curl -X POST https://<API_URL>/v1/orders \
  -H "Authorization: Bearer <ID_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "total_amount": 99.99,
    "status": "PENDING",
    "items": [
      {"product_id": "prod-1", "quantity": 2, "price": 49.99}
    ]
  }'
```

## 💰 Costes Estimados

Estimación mensual para **tráfico bajo** (< 10K requests/mes):

| Servicio | Coste Mensual |
|----------|---------------|
| Lambda | < 1 € |
| API Gateway | < 3 € |
| DynamoDB (on-demand) | < 2 € |
| CloudWatch Logs | < 1 € |
| Cognito | Gratis (< 50K MAU) |
| **Total** | **~5-7 €/mes** |

### Escalabilidad

- **10x tráfico** (100K requests): ~15-20 €/mes
- **100x tráfico** (1M requests): ~50-70 €/mes

El sistema escala automáticamente sin cambios arquitectónicos gracias a:
- Lambda auto-scaling
- DynamoDB on-demand
- API Gateway managed

## 🗂️ Estructura del Proyecto

```
orders-serverless-api/
│
├── infra/                      # Infraestructura como código
│   ├── main.tf                # Configuración principal de Terraform
│   ├── variables.tf           # Variables configurables
│   ├── outputs.tf             # Outputs del deployment
│   ├── api_gateway.tf         # API Gateway + endpoints
│   ├── lambda.tf              # Lambda function
│   ├── dynamodb.tf            # Tabla DynamoDB
│   ├── iam.tf                 # Roles y policies
│   ├── cognito.tf             # User Pool y cliente
│   └── environments/
│       ├── dev.tfvars         # Config de desarrollo
│       └── prod.tfvars        # Config de producción
│
├── src/orders/                # Código Lambda
│   ├── handler.py             # Handler principal
│   ├── models.py              # Modelos de dominio
│   ├── repository.py          # Capa de acceso a datos
│   └── requirements.txt       # Dependencias Python
│
├── docs/                      # Documentación
│   └── decisions.md           # Decisiones arquitectónicas
│
├── tests/                     # 🧪 NEW: Test suite completa
│   ├── unit/                  # Tests unitarios (40+ tests)
│   ├── integration/           # Tests E2E (10+ tests)
│   ├── conftest.py            # Fixtures compartidas
│   └── requirements.txt       # Dependencias de tests
│
├── .github/workflows/         # 🔄 NEW: CI/CD automation
│   └── tests.yml              # GitHub Actions pipeline
│
├── pytest.ini                 # 🧪 NEW: Configuración pytest
├── .coveragerc                # 📊 NEW: Configuración coverage
├── .pre-commit-config.yaml    # 🔍 NEW: Pre-commit hooks
│
└── README.md                  # Este archivo
```

## 🧪 Testing (Phase 2)

### Ejecutar Tests

```bash
# Instalar dependencias
pip install -r tests/requirements.txt

# Todos los tests
pytest

# Solo unit tests (rápidos)
pytest tests/unit/

# Con coverage
pytest --cov=src/orders --cov-report=html
```

### Coverage Actual
- **50+ test cases** (unit + integration)
- **~80-85% code coverage**
- Tests automatizados en CI/CD

Ver [docs/TESTING.md](docs/TESTING.md) para guía completa.

## 🎯 Decisiones Técnicas

### ¿Por qué Python?
- Excelente soporte para serverless en AWS
- Rápido desarrollo
- Librería boto3 nativa
- Ideal para APIs REST

### ¿Por qué Terraform?
- Infraestructura reproducible
- Versionado de infra
- Multi-entorno (dev/prod)
- Muy demandado en el mercado

### ¿Por qué DynamoDB?
- Zero mantenimiento
- Escala automática
- Pay-per-request perfecto para serverless
- Performance predecible

### ¿Por qué Cognito?
- Manejo de JWT automático
- Integración nativa con API Gateway
- Evita implementar auth custom
- Altamente escalable

## 📊 Observabilidad

### Logs

```bash
# Ver logs de Lambda
aws logs tail /aws/lambda/orders-api-dev-orders-api --follow

# Ver logs de API Gateway
aws logs tail /aws/apigateway/orders-api-dev --follow
```

### Métricas en CloudWatch

- Request count
- Error rate (4xx, 5xx)
- Latency (p50, p95, p99)
- Throttles
- DynamoDB consumed capacity

### Alarmas (recomendado para producción)

```hcl
# Agregar a infra/ para alarmas
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${local.resource_prefix}-api-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "API Gateway 5xx errors"
}
```

## 🔧 Desarrollo Local

### Testing manual

1. Deployar a dev: `terraform apply -var-file=environments/dev.tfvars`
2. Crear usuario de prueba (ver sección de Autenticación)
3. Obtener token JWT
4. Hacer requests con Postman/curl

### Variables de entorno para Lambda

La Lambda recibe automáticamente:
- `DYNAMODB_TABLE`: Nombre de la tabla
- `ENVIRONMENT`: dev o prod
- `LOG_LEVEL`: DEBUG en dev, INFO en prod

## 🚨 Troubleshooting

### Error: "User is not authenticated"
→ Verifica que el token JWT esté en el header `Authorization: Bearer <token>`

### Error: "Access Denied" en DynamoDB
→ Revisa los permisos IAM en `iam.tf`

### Lambda timeout
→ Aumenta el timeout en `lambda.tf` (default: 30s)

### Cognito domain ya existe
→ El dominio debe ser globalmente único. Terraform usa un suffix random automáticamente.

## 📚 Próximos pasos (mejoras opcionales)

- [ ] Tests unitarios con pytest
- [ ] CI/CD con GitHub Actions
- [ ] OpenAPI/Swagger documentation
- [ ] Métricas custom
- [ ] Alarmas de CloudWatch
- [ ] DynamoDB Streams para eventos
- [ ] ElastiCache para caché
- [ ] WAF para seguridad adicional

## 📄 Licencia

MIT

---

**Desarrollado con**: Python 3.11 | Terraform | AWS Serverless
