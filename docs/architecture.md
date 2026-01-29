# Arquitectura del Sistema

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT / FRONTEND                        │
│                  (Web, Mobile, Postman, cURL)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS + JWT Token
                         │ Authorization: Bearer <token>
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (REST)                          │
│                                                                  │
│  • Endpoints: /v1/orders, /v1/orders/{id}                      │
│  • Methods: GET, POST, PUT, DELETE                             │
│  • Rate Limiting: 50-250 req/s                                 │
│  • Usage Plans & API Keys                                      │
│  • CloudWatch Logs                                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   COGNITO JWT AUTHORIZER                         │
│                                                                  │
│  • Valida JWT Token                                            │
│  • Extrae claims (sub, email, etc.)                           │
│  • Autoriza o rechaza request                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Authorized
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA (Python 3.11)                      │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  handler.py                                              │  │
│  │  • Routing HTTP                                          │  │
│  │  • Validación de input                                   │  │
│  │  • Manejo de errores                                     │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  models.py                                               │  │
│  │  • Order (domain model)                                  │  │
│  │  • OrderStatus (enum)                                    │  │
│  │  • Validación de negocio                                 │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│  ┌──────────────▼───────────────────────────────────────────┐  │
│  │  repository.py                                           │  │
│  │  • CRUD operations                                       │  │
│  │  • DynamoDB client (boto3)                               │  │
│  │  • Query builders                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Environment Variables:                                         │
│  • DYNAMODB_TABLE                                              │
│  • ENVIRONMENT (dev/prod)                                      │
│  • LOG_LEVEL                                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ boto3 SDK
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AMAZON DYNAMODB                               │
│                                                                  │
│  Table: orders-api-{env}-orders                                │
│                                                                  │
│  Primary Key:                                                   │
│  • order_id (Partition Key)                                    │
│                                                                  │
│  Global Secondary Index (GSI):                                  │
│  • CustomerIndex                                               │
│    - customer_id (PK)                                          │
│    - created_at (Sort Key)                                     │
│                                                                  │
│  Attributes:                                                    │
│  • order_id, customer_id, status                               │
│  • total_amount, created_at, updated_at                        │
│  • items (list)                                                │
│                                                                  │
│  Features:                                                      │
│  • On-demand billing                                           │
│  • Server-side encryption                                      │
│  • Point-in-time recovery (prod)                               │
└─────────────────────────────────────────────────────────────────┘

                         ┌───────────────────┐
                         │                   │
                         │   CLOUDWATCH      │
                         │                   │
                         │  • Lambda Logs    │
                         │  • API Logs       │
                         │  • Metrics        │
                         │  • Alarms         │
                         │                   │
                         └───────────────────┘

                         ┌───────────────────┐
                         │                   │
                         │  COGNITO          │
                         │  USER POOL        │
                         │                   │
                         │  • Users DB       │
                         │  • Password       │
                         │    Policy         │
                         │  • JWT Tokens     │
                         │                   │
                         └───────────────────┘
```

## Flujo de una Request

### POST /v1/orders (Crear pedido)

```
1. Cliente                                    4. Lambda
   │                                             │
   │ POST /v1/orders                             │ 1. Parse request
   │ Auth: Bearer xyz123                         │ 2. Validate input
   │ Body: { customer_id, ... }                  │ 3. Create Order model
   │                                             │ 4. order.validate()
   ▼                                             │ 5. repository.create_order()
2. API Gateway                                   │
   │                                             ▼
   │ 1. Rate limit check                      5. DynamoDB
   │ 2. Validate request                         │
   ▼                                             │ 1. PutItem
3. Cognito Authorizer                            │ 2. Return success
   │                                             │
   │ 1. Decode JWT                               ▼
   │ 2. Verify signature                      6. Lambda Response
   │ 3. Check expiration                         │
   │ 4. Extract claims                           │ { order_id, status: 201 }
   │                                             │
   │ ✓ Allow                                     ▼
   ▼                                          7. API Gateway
4. Lambda invoked                                │
   with event                                    │ Add CORS headers
                                                 │
                                                 ▼
                                              8. Cliente recibe
                                                 201 Created + order_id
```

### GET /v1/orders?customer_id=X (Listar pedidos)

```
1. Cliente → API Gateway → Cognito → Lambda

2. Lambda:
   - Parse query params
   - Call repository.list_orders(customer_id)

3. DynamoDB:
   - Query GSI: CustomerIndex
   - Filter by customer_id
   - Sort by created_at DESC
   - Return items

4. Lambda → Format response → API Gateway → Cliente
   { orders: [...], count: 5 }
```

## Seguridad en capas

```
┌────────────────────────────────────────────────┐
│ Layer 1: HTTPS (TLS 1.2+)                     │
│ • Encriptación en tránsito                    │
└────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────┐
│ Layer 2: API Gateway Rate Limiting            │
│ • Throttling: 50-250 req/s                    │
│ • Usage plans                                 │
└────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────┐
│ Layer 3: Cognito JWT Authorizer               │
│ • Token validation                            │
│ • User authentication                         │
└────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────┐
│ Layer 4: IAM Roles (Least Privilege)          │
│ • Lambda → DynamoDB: solo esta tabla          │
│ • Lambda → CloudWatch: solo logs              │
└────────────────────────────────────────────────┘
                    ▼
┌────────────────────────────────────────────────┐
│ Layer 5: DynamoDB Encryption at Rest          │
│ • Server-side encryption (SSE)                │
└────────────────────────────────────────────────┘
```

## Escalabilidad

```
                     ┌─────────────┐
                     │   1 request │
                     └──────┬──────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    │   API Gateway         │    Lambda             │
    │   (managed)           │    (1 instance)       │
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                            │
                     ┌──────▼──────┐
                     │   DynamoDB  │
                     │  (on-demand)│
                     └─────────────┘


                     ┌─────────────┐
                     │ 1000 req/s  │
                     └──────┬──────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
    │   API Gateway         │    Lambda             │
    │   (auto-scale)        │    (100+ instances)   │
    │                       │    AUTO SCALE         │
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                            │ Parallel writes
                     ┌──────▼──────┐
                     │   DynamoDB  │
                     │  (scales up)│
                     │  AUTO SCALE │
                     └─────────────┘

✅ Sin cambios de código
✅ Sin configuración manual
✅ Coste proporcional al uso
```

## Costes por componente

```
┌─────────────────────────────────────────────────────┐
│ API Gateway                                         │
│ • 10K requests → ~0.035€                            │
│ • 100K requests → ~0.35€                            │
│ • 1M requests → ~3.50€                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Lambda                                              │
│ • 10K requests (200ms avg) → ~0.01€                 │
│ • 100K requests → ~0.10€                            │
│ • 1M requests → ~1.00€                              │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ DynamoDB (on-demand)                                │
│ • 10K reads + 10K writes → ~0.50€                   │
│ • 100K reads + 100K writes → ~5.00€                 │
│ • Storage: 1GB → ~0.25€/mes                         │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ CloudWatch                                          │
│ • 5GB logs/mes → gratis                             │
│ • 10 alarmas → ~1.00€                               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Cognito                                             │
│ • < 50K MAU → GRATIS                                │
└─────────────────────────────────────────────────────┘

Total 10K requests/mes:   ~1€
Total 100K requests/mes:  ~6€
Total 1M requests/mes:    ~10€
```

## Deploy Pipeline (Manual)

```
Developer
   │
   │ 1. Modify code/infra
   │
   ▼
Local Git Commit
   │
   │ 2. git push
   │
   ▼
GitHub Repository
   │
   │ 3. cd infra
   │ 4. terraform plan
   │
   ▼
Review Changes
   │
   │ 5. terraform apply
   │
   ▼
AWS Resources
   │
   ├──▶ API Gateway (updated)
   ├──▶ Lambda (new version)
   ├──▶ DynamoDB (updated)
   └──▶ Cognito (updated)
   │
   ▼
Production Live ✅

Tiempo estimado: 5-10 minutos
```

## Próximas mejoras (roadmap)

```
Phase 2 - Observabilidad
├─ CloudWatch Alarms
├─ X-Ray tracing
├─ Custom metrics
└─ Dashboards

Phase 3 - CI/CD
├─ GitHub Actions
├─ Automated tests
├─ Pre-prod environment
└─ Blue/green deployment

Phase 4 - Performance
├─ DynamoDB DAX cache
├─ ElastiCache (Redis)
├─ Lambda provisioned concurrency
└─ API Gateway caching

Phase 5 - Eventos
├─ DynamoDB Streams
├─ EventBridge
├─ SNS notifications
└─ SQS queues
```
