# Orders Serverless API - Quick Start

## 🚀 Deploy en 3 pasos

### 1. Configurar AWS CLI
```bash
aws configure
# AWS Access Key ID: tu-access-key
# AWS Secret Access Key: tu-secret-key
# Default region: eu-west-1
```

### 2. Deployar infraestructura
```bash
cd infra
terraform init
terraform apply -var-file=environments/dev.tfvars
```

### 3. Crear usuario y obtener token
```bash
# Guarda los outputs
API_URL=$(terraform output -raw api_gateway_url)
USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)

# Crear usuario
aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Establecer contraseña permanente
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username admin@example.com \
  --password MySecurePass123! \
  --permanent

# Obtener token
TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id $CLIENT_ID \
  --auth-parameters USERNAME=admin@example.com,PASSWORD=MySecurePass123! \
  --query 'AuthenticationResult.IdToken' \
  --output text)
```

### 4. Probar la API
```bash
# Crear order
curl -X POST $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "total_amount": 150.50,
    "status": "PENDING",
    "items": [
      {"product_id": "prod-1", "quantity": 2, "price": 75.25}
    ]
  }'

# Listar orders
curl -X GET $API_URL/v1/orders \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Ver logs

```bash
# Logs de Lambda
aws logs tail /aws/lambda/orders-api-dev-orders-api --follow

# Logs de API Gateway
aws logs tail /aws/apigateway/orders-api-dev --follow
```

## 🧹 Limpiar recursos

```bash
cd infra
terraform destroy -var-file=environments/dev.tfvars
```

---

**Coste estimado**: ~5-7 €/mes con tráfico bajo

**Stack**: Python 3.11 | Terraform | Lambda | API Gateway | DynamoDB | Cognito
