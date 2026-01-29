# 📂 Estructura del Proyecto

```
orders-serverless-api/
│
├── 📄 README.md                    ← Documentación principal
├── 📄 LICENSE                      ← Licencia MIT
├── 📄 .gitignore                   ← Archivos ignorados
├── 📄 Makefile                     ← Comandos helper (Linux/Mac)
├── 📄 scripts.ps1                  ← Scripts PowerShell (Windows)
│
├── 📁 infra/                       ← Infraestructura como código (Terraform)
│   │
│   ├── 🔧 main.tf                  ← Configuración principal + providers
│   ├── 🔧 variables.tf             ← Variables del proyecto
│   ├── 🔧 outputs.tf               ← Outputs (API URL, IDs, etc.)
│   │
│   ├── 🔧 api_gateway.tf           ← REST API + endpoints + stages
│   ├── 🔧 lambda.tf                ← Lambda function + logs + permissions
│   ├── 🔧 dynamodb.tf              ← Tabla orders + GSI
│   ├── 🔧 cognito.tf               ← User Pool + Client + Domain
│   ├── 🔧 iam.tf                   ← Roles + Policies
│   │
│   └── 📁 environments/
│       ├── dev.tfvars              ← Config desarrollo
│       └── prod.tfvars             ← Config producción
│
├── 📁 src/                         ← Código fuente Lambda
│   └── 📁 orders/
│       ├── 🐍 handler.py           ← Lambda handler (routing HTTP)
│       ├── 🐍 models.py            ← Domain models (Order, OrderStatus)
│       ├── 🐍 repository.py        ← Data access layer (DynamoDB)
│       └── 📄 requirements.txt     ← Dependencias Python (boto3)
│
└── 📁 docs/                        ← Documentación extendida
    ├── 📖 QUICKSTART.md            ← Deploy en 3 pasos (5 min)
    ├── 📖 WINDOWS_GUIDE.md         ← Guía completa para Windows
    ├── 📖 EXECUTIVE_SUMMARY.md     ← Resumen para recruiters
    ├── 📖 architecture.md          ← Diagramas y flujos
    ├── 📖 decisions.md             ← ADRs (decisiones arquitectónicas)
    └── 📖 API_EXAMPLES.md          ← Ejemplos de uso completos
```

---

## 🎯 Flujo de Archivos

### 1. Deployment Flow

```
developer
    ↓
infra/*.tf
    ↓
terraform apply
    ↓
AWS Resources Created
    ├─ API Gateway
    ├─ Lambda (packaged from src/orders/)
    ├─ DynamoDB
    ├─ Cognito
    └─ IAM Roles
```

### 2. Request Flow

```
Client
    ↓
API Gateway (api_gateway.tf)
    ↓
Cognito Authorizer (cognito.tf)
    ↓
Lambda Function (lambda.tf)
    ├─ handler.py (route request)
    ├─ models.py (validate data)
    └─ repository.py (query DynamoDB)
    ↓
DynamoDB Table (dynamodb.tf)
```

### 3. Development Flow

```
1. Modify code: src/orders/*.py
2. Test locally (optional)
3. Modify infra: infra/*.tf
4. Plan: terraform plan -var-file=environments/dev.tfvars
5. Apply: terraform apply
6. Lambda auto-updates with new code
```

---

## 📋 Archivos Clave

### Infrastructure (Terraform)

| Archivo | Propósito | LOC |
|---------|-----------|-----|
| `main.tf` | Provider config + backend | ~40 |
| `variables.tf` | Input variables | ~45 |
| `outputs.tf` | Export values | ~35 |
| `api_gateway.tf` | REST API + 5 endpoints | ~200 |
| `lambda.tf` | Function + logs + packaging | ~60 |
| `dynamodb.tf` | Table + GSI | ~50 |
| `cognito.tf` | User Pool + Client | ~60 |
| `iam.tf` | Roles + Policies | ~80 |
| **Total** | **~570 LOC** | |

### Application (Python)

| Archivo | Propósito | LOC |
|---------|-----------|-----|
| `handler.py` | HTTP routing + Lambda handler | ~180 |
| `models.py` | Domain model (Order) | ~70 |
| `repository.py` | DynamoDB operations | ~120 |
| `requirements.txt` | Dependencies | ~1 |
| **Total** | **~370 LOC** | |

### Documentation

| Archivo | Propósito | Páginas |
|---------|-----------|---------|
| `README.md` | Main docs | 300 líneas |
| `QUICKSTART.md` | Fast start | 100 líneas |
| `WINDOWS_GUIDE.md` | Windows setup | 300 líneas |
| `EXECUTIVE_SUMMARY.md` | For recruiters | 250 líneas |
| `architecture.md` | Diagrams | 400 líneas |
| `decisions.md` | ADRs | 300 líneas |
| `API_EXAMPLES.md` | Usage examples | 400 líneas |
| **Total** | **~2000 líneas** | |

---

## 🔄 Dependencias entre Archivos

### Terraform Dependencies

```
main.tf (provider)
    ↓
variables.tf
    ↓
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
iam.tf     cognito.tf    dynamodb.tf    api_gateway.tf
│              │              │              │
└──────────────┴──────────────┴──────────────┘
                ↓
            lambda.tf
                ↓
            outputs.tf
```

### Python Dependencies

```
handler.py
    ├─ import models
    └─ import repository
        └─ import boto3 (from requirements.txt)
```

---

## 📦 Artifacts Generados

Durante el deployment, Terraform genera:

```
infra/
├── .terraform/               ← Providers descargados
│   └── providers/
│       └── hashicorp/
│           ├── aws/
│           ├── archive/
│           └── random/
│
├── terraform.tfstate         ← Estado actual (SENSIBLE)
├── terraform.tfstate.backup  ← Backup del estado anterior
├── .terraform.lock.hcl       ← Lock de versiones de providers
└── lambda_function.zip       ← Código Lambda empaquetado
```

⚠️ **No commitar:** `.terraform/`, `*.tfstate`, `lambda_function.zip`

---

## 🎨 Convenciones de Código

### Python (PEP 8)

```python
# handler.py
def lambda_handler(event, context):
    """Main Lambda handler"""
    # 4 espacios de indentación
    # Docstrings en funciones públicas
    # Type hints donde sea posible

# models.py
class Order:
    """Order domain model"""
    # CamelCase para clases
    # snake_case para funciones/variables

# repository.py
class OrderRepository:
    """DynamoDB repository for orders"""
    # Métodos descriptivos
    # Error handling explícito
```

### Terraform (HashiCorp Style)

```hcl
# main.tf
resource "aws_lambda_function" "orders_api" {
  # snake_case para nombres de recursos
  # 2 espacios de indentación
  # Comentarios explicativos

  tags = {
    Name = "${local.resource_prefix}-orders-api"
    # Tags consistentes
  }
}
```

---

## 🔍 Búsqueda Rápida

### Encontrar configuración de...

- **Lambda timeout**: `infra/lambda.tf` → línea ~20
- **DynamoDB table name**: `infra/dynamodb.tf` → línea ~2
- **API rate limits**: `infra/api_gateway.tf` → línea ~150
- **Cognito password policy**: `infra/cognito.tf` → línea ~5
- **Environment variables**: `infra/lambda.tf` → línea ~25

### Encontrar lógica de...

- **Crear order**: `src/orders/handler.py` → función `handle_create_order`
- **Validación**: `src/orders/models.py` → método `validate()`
- **Query DynamoDB**: `src/orders/repository.py` → método `list_orders()`
- **Error handling**: `src/orders/handler.py` → funciones `*_response()`

---

## 📊 Métricas del Proyecto

```
Total archivos:      25+
Total líneas:        ~3000 (código + docs)
Lenguajes:           Python, HCL (Terraform), Markdown
Cobertura docs:      100%
Tests:               0 (próxima fase)
Environments:        2 (dev, prod)
AWS Services:        6 (Lambda, API GW, DDB, Cognito, IAM, CloudWatch)
Deployment time:     < 10 minutos
Monthly cost:        ~5-7 € (low traffic)
```

---

## 🎯 Orden de Lectura Recomendado

### Para empezar rápido:
1. [README.md](../README.md) - Overview
2. [docs/QUICKSTART.md](QUICKSTART.md) - Deploy en 5 min
3. [docs/WINDOWS_GUIDE.md](WINDOWS_GUIDE.md) - Si usas Windows

### Para entender la arquitectura:
1. [docs/EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Visión de alto nivel
2. [docs/architecture.md](architecture.md) - Diagramas detallados
3. [docs/decisions.md](decisions.md) - Por qué se tomaron decisiones

### Para usar la API:
1. [docs/API_EXAMPLES.md](API_EXAMPLES.md) - Ejemplos completos
2. `infra/api_gateway.tf` - Ver definición de endpoints
3. `src/orders/handler.py` - Ver implementación

### Para modificar el proyecto:
1. `infra/*.tf` - Modificar infraestructura
2. `src/orders/*.py` - Modificar lógica
3. `docs/decisions.md` - Documentar tus decisiones

---

## ✅ Checklist de Archivos Completos

- [x] `README.md` - Documentación principal
- [x] `LICENSE` - Licencia MIT
- [x] `.gitignore` - Ignora archivos sensibles
- [x] `Makefile` - Helper commands (Unix)
- [x] `scripts.ps1` - Helper commands (Windows)
- [x] `infra/main.tf` - Terraform config
- [x] `infra/variables.tf` - Variables
- [x] `infra/outputs.tf` - Outputs
- [x] `infra/api_gateway.tf` - API Gateway
- [x] `infra/lambda.tf` - Lambda
- [x] `infra/dynamodb.tf` - DynamoDB
- [x] `infra/cognito.tf` - Cognito
- [x] `infra/iam.tf` - IAM
- [x] `infra/environments/dev.tfvars` - Dev config
- [x] `infra/environments/prod.tfvars` - Prod config
- [x] `src/orders/handler.py` - Lambda handler
- [x] `src/orders/models.py` - Domain models
- [x] `src/orders/repository.py` - Data access
- [x] `src/orders/requirements.txt` - Dependencies
- [x] `docs/QUICKSTART.md` - Quick start guide
- [x] `docs/WINDOWS_GUIDE.md` - Windows guide
- [x] `docs/EXECUTIVE_SUMMARY.md` - Executive summary
- [x] `docs/architecture.md` - Architecture docs
- [x] `docs/decisions.md` - ADRs
- [x] `docs/API_EXAMPLES.md` - API examples

**✅ Proyecto 100% completo y listo para usar!**
