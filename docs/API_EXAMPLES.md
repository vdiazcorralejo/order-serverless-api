# Ejemplos de Uso de la API

## Setup inicial

```bash
# Variables de entorno (obtener después de terraform apply)
export API_URL="https://xxxxxxxxxx.execute-api.eu-west-1.amazonaws.com/dev"
export USER_POOL_ID="eu-west-1_XXXXXXXX"
export CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxx"

# Token JWT (obtener después de login)
export TOKEN="eyJraWQiOiJ..."
```

---

## 1. Crear un pedido

### Request

```bash
curl -X POST $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "total_amount": 99.99,
    "status": "PENDING",
    "items": [
      {
        "product_id": "prod-001",
        "name": "Laptop Dell XPS 13",
        "quantity": 1,
        "price": 99.99
      }
    ]
  }'
```

### Response (201 Created)

```json
{
  "order_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "customer_id": "customer-123",
  "status": "PENDING",
  "total_amount": 99.99,
  "created_at": "2026-01-29T10:30:00.000Z",
  "updated_at": "2026-01-29T10:30:00.000Z",
  "items": [
    {
      "product_id": "prod-001",
      "name": "Laptop Dell XPS 13",
      "quantity": 1,
      "price": 99.99
    }
  ]
}
```

---

## 2. Obtener un pedido por ID

### Request

```bash
ORDER_ID="a1b2c3d4-5678-90ab-cdef-1234567890ab"

curl -X GET $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Response (200 OK)

```json
{
  "order_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "customer_id": "customer-123",
  "status": "PENDING",
  "total_amount": 99.99,
  "created_at": "2026-01-29T10:30:00.000Z",
  "updated_at": "2026-01-29T10:30:00.000Z",
  "items": [...]
}
```

### Error - Pedido no encontrado (404)

```json
{
  "error": "Order not found",
  "timestamp": "2026-01-29T10:35:00.000Z"
}
```

---

## 3. Listar todos los pedidos

### Request

```bash
curl -X GET $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN"
```

### Response (200 OK)

```json
{
  "orders": [
    {
      "order_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "customer_id": "customer-123",
      "status": "PENDING",
      "total_amount": 99.99,
      "created_at": "2026-01-29T10:30:00.000Z",
      "updated_at": "2026-01-29T10:30:00.000Z",
      "items": [...]
    },
    {
      "order_id": "b2c3d4e5-6789-01bc-def2-234567890abc",
      "customer_id": "customer-456",
      "status": "COMPLETED",
      "total_amount": 249.99,
      "created_at": "2026-01-29T09:15:00.000Z",
      "updated_at": "2026-01-29T09:45:00.000Z",
      "items": [...]
    }
  ],
  "count": 2
}
```

---

## 4. Listar pedidos de un cliente específico

### Request

```bash
curl -X GET "$API_URL/v1/orders?customer_id=customer-123" \
  -H "Authorization: Bearer $TOKEN"
```

### Response (200 OK)

```json
{
  "orders": [
    {
      "order_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "customer_id": "customer-123",
      "status": "PENDING",
      "total_amount": 99.99,
      "created_at": "2026-01-29T10:30:00.000Z",
      "updated_at": "2026-01-29T10:30:00.000Z",
      "items": [...]
    }
  ],
  "count": 1
}
```

---

## 5. Actualizar un pedido

### Request - Cambiar estado

```bash
curl -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "PROCESSING"
  }'
```

### Request - Actualizar total y items

```bash
curl -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "PROCESSING",
    "total_amount": 149.99,
    "items": [
      {
        "product_id": "prod-001",
        "name": "Laptop Dell XPS 13",
        "quantity": 1,
        "price": 99.99
      },
      {
        "product_id": "prod-002",
        "name": "Mouse Logitech MX",
        "quantity": 1,
        "price": 50.00
      }
    ]
  }'
```

### Response (200 OK)

```json
{
  "order_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "customer_id": "customer-123",
  "status": "PROCESSING",
  "total_amount": 149.99,
  "created_at": "2026-01-29T10:30:00.000Z",
  "updated_at": "2026-01-29T10:45:00.000Z",
  "items": [...]
}
```

---

## 6. Eliminar un pedido

### Request

```bash
curl -X DELETE $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Response (200 OK)

```json
{
  "message": "Order deleted successfully"
}
```

---

## 7. Manejo de errores

### Sin token (401 Unauthorized)

```bash
curl -X GET $API_URL/v1/orders
```

**Response:**
```json
{
  "message": "Unauthorized"
}
```

### Token inválido (401 Unauthorized)

```bash
curl -X GET $API_URL/v1/orders \
  -H "Authorization: Bearer invalid_token"
```

**Response:**
```json
{
  "message": "Unauthorized"
}
```

### Validación fallida (400 Bad Request)

```bash
curl -X POST $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "total_amount": -50,
    "status": "INVALID_STATUS"
  }'
```

**Response:**
```json
{
  "error": "Validation errors: total_amount must be greater than 0",
  "timestamp": "2026-01-29T10:50:00.000Z"
}
```

### Rate limit exceeded (429 Too Many Requests)

Cuando se superan los límites configurados:

```json
{
  "message": "Too Many Requests"
}
```

---

## 8. Estados de pedido (workflow)

```
PENDING → PROCESSING → COMPLETED
   ↓
CANCELLED
```

### Crear como PENDING

```bash
curl -X POST $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "c1", "total_amount": 100, "status": "PENDING"}'
```

### Mover a PROCESSING

```bash
curl -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "PROCESSING"}'
```

### Completar

```bash
curl -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "COMPLETED"}'
```

### Cancelar

```bash
curl -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "CANCELLED"}'
```

---

## 9. Testing con Postman

### Colección de variables

```json
{
  "api_url": "{{API_URL}}",
  "token": "{{TOKEN}}",
  "order_id": "{{ORDER_ID}}"
}
```

### Pre-request Script (obtener token automáticamente)

```javascript
// Guardar en Postman Environment:
// - cognito_client_id
// - cognito_username
// - cognito_password

const clientId = pm.environment.get("cognito_client_id");
const username = pm.environment.get("cognito_username");
const password = pm.environment.get("cognito_password");

// Obtener token (requiere AWS CLI o API directa)
// Alternativamente, actualizar manualmente cada hora
```

---

## 10. Script completo de prueba

```bash
#!/bin/bash

# Script de prueba completo para Orders API

# 1. Variables
API_URL="https://your-api-url.execute-api.eu-west-1.amazonaws.com/dev"
TOKEN="your-jwt-token-here"

echo "🧪 Testing Orders API"
echo "===================="

# 2. Crear pedido
echo -e "\n1️⃣ Creating order..."
RESPONSE=$(curl -s -X POST $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "test-customer-001",
    "total_amount": 199.99,
    "status": "PENDING",
    "items": [{"product_id": "prod-123", "quantity": 1, "price": 199.99}]
  }')

ORDER_ID=$(echo $RESPONSE | jq -r '.order_id')
echo "✅ Order created: $ORDER_ID"

# 3. Obtener pedido
echo -e "\n2️⃣ Getting order..."
curl -s -X GET $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Listar pedidos
echo -e "\n3️⃣ Listing orders..."
curl -s -X GET $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" | jq

# 5. Actualizar pedido
echo -e "\n4️⃣ Updating order..."
curl -s -X PUT $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "PROCESSING"}' | jq

# 6. Eliminar pedido
echo -e "\n5️⃣ Deleting order..."
curl -s -X DELETE $API_URL/v1/orders/$ORDER_ID \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n✅ All tests completed!"
```

---

## 11. Performance testing con Apache Bench

```bash
# Crear archivo con payload
cat > order_payload.json <<EOF
{
  "customer_id": "perf-test",
  "total_amount": 100,
  "status": "PENDING",
  "items": []
}
EOF

# Test de carga (requiere token válido)
ab -n 1000 -c 10 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -p order_payload.json \
  $API_URL/v1/orders
```

---

## 12. Monitoreo con CloudWatch Logs

```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/orders-api-dev-orders-api --follow

# Buscar errores
aws logs filter-log-events \
  --log-group-name /aws/lambda/orders-api-dev-orders-api \
  --filter-pattern "ERROR"

# Ver métricas
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=orders-api-dev-orders-api \
  --start-time 2026-01-29T00:00:00Z \
  --end-time 2026-01-29T23:59:59Z \
  --period 3600 \
  --statistics Sum
```
