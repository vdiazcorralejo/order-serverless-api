# ✅ Checklist de Verificación Pre-Deploy

Usa este checklist antes de hacer deploy para asegurar que todo está configurado correctamente.

---

## 📋 Pre-requisitos

### 1. AWS CLI Configurado

```powershell
# Verificar instalación
aws --version
# Debería mostrar: aws-cli/2.x.x

# Verificar configuración
aws sts get-caller-identity
# Debería mostrar tu Account ID y User/Role
```

✅ **OK si ves tu información de AWS**
❌ **ERROR**: Ejecuta `aws configure` para configurar credenciales

---

### 2. Terraform Instalado

```powershell
# Verificar instalación
terraform version
# Debería mostrar: Terraform v1.x.x
```

✅ **OK si versión >= 1.0**
❌ **ERROR**: Descarga desde [terraform.io](https://www.terraform.io/downloads)

---

### 3. Permisos AWS Necesarios

Tu usuario/rol de AWS necesita permisos para:

- ✅ Lambda (create, update, invoke)
- ✅ API Gateway (create, update, deploy)
- ✅ DynamoDB (create table, create GSI)
- ✅ Cognito (create user pool, create client)
- ✅ IAM (create role, attach policy)
- ✅ CloudWatch (create log groups)

**Test rápido:**

```powershell
# Intentar listar lambdas (si tienes alguna)
aws lambda list-functions

# Si da error de permisos, contacta a tu admin AWS
```

---

## 🔍 Validación de Archivos

### 1. Verificar Estructura del Proyecto

```powershell
# Desde la raíz del proyecto
Get-ChildItem -Recurse -Depth 2 | Select-Object FullName
```

**Deberías ver:**
```
infra/
  ├── main.tf
  ├── variables.tf
  ├── outputs.tf
  ├── api_gateway.tf
  ├── lambda.tf
  ├── dynamodb.tf
  ├── cognito.tf
  ├── iam.tf
  └── environments/
      ├── dev.tfvars
      └── prod.tfvars
src/
  └── orders/
      ├── handler.py
      ├── models.py
      ├── repository.py
      └── requirements.txt
docs/
  ├── QUICKSTART.md
  ├── WINDOWS_GUIDE.md
  ├── ...
```

---

### 2. Validar Sintaxis Python

```powershell
# Verificar sintaxis de Python
python -m py_compile src\orders\handler.py
python -m py_compile src\orders\models.py
python -m py_compile src\orders\repository.py
```

✅ **OK si no hay output (sin errores)**
❌ **ERROR**: Corrige los errores de sintaxis mostrados

---

### 3. Validar Terraform

```powershell
cd infra

# Formatear archivos (auto-fix)
terraform fmt

# Validar sintaxis
terraform validate
```

✅ **OK si dice "Success! The configuration is valid."**
❌ **ERROR**: Corrige los errores mostrados

---

## 🚀 Pre-Deploy Checklist

### Paso 1: Inicializar Terraform

```powershell
cd infra
terraform init
```

**Deberías ver:**
```
Initializing the backend...
Initializing provider plugins...
- Installing hashicorp/aws v5.x.x...
- Installing hashicorp/archive v2.x.x...
- Installing hashicorp/random v3.x.x...

Terraform has been successfully initialized!
```

✅ **OK**
❌ **ERROR**: Revisa conexión a internet y permisos

---

### Paso 2: Review Plan

```powershell
# Ver qué recursos se van a crear
terraform plan -var-file="environments\dev.tfvars"
```

**Deberías ver algo como:**
```
Plan: 25 to add, 0 to change, 0 to destroy.
```

**Recursos esperados (~25):**
- 1 DynamoDB table
- 1 Lambda function
- 1 API Gateway REST API
- Multiple API Gateway resources/methods/integrations
- 1 Cognito User Pool
- 1 Cognito User Pool Client
- 1 Cognito Domain
- IAM roles and policies
- CloudWatch log groups
- Lambda permission

✅ **OK si muestra ~20-30 recursos a crear**
⚠️ **WARNING**: Si muestra "destroy", revisa qué va a eliminar
❌ **ERROR**: Corrige los errores de validación

---

### Paso 3: Verificar Variables

```powershell
# Ver valores de variables
cat infra\environments\dev.tfvars
```

**Verificar:**
- ✅ `environment = "dev"` (o "prod")
- ✅ `aws_region = "eu-west-1"` (o tu región preferida)
- ✅ Rate limits configurados
- ✅ Tags apropiados

---

### Paso 4: Estimar Costes (Opcional)

Si tienes [infracost](https://www.infracost.io/) instalado:

```powershell
cd infra
infracost breakdown --path .
```

**Coste esperado:** ~5-7 €/mes para tráfico bajo

---

## 🎯 Deploy!

```powershell
cd infra
terraform apply -var-file="environments\dev.tfvars"
```

**Durante el apply:**

1. ⏱️ **~5-10 minutos** de duración
2. 📦 Empaqueta el código Lambda (crea lambda_function.zip)
3. 🚀 Crea todos los recursos en AWS
4. 📊 Muestra outputs al final

**Outputs esperados:**
```
Outputs:

api_gateway_url = "https://xxxxxxxxxx.execute-api.eu-west-1.amazonaws.com/dev"
cognito_user_pool_id = "eu-west-1_XXXXXXXXX"
cognito_user_pool_client_id = "xxxxxxxxxxxxxxxxxxxxxxxxxx"
dynamodb_table_name = "orders-api-dev-orders"
lambda_function_name = "orders-api-dev-orders-api"
```

✅ **Guarda estos valores!** Los necesitarás para testing

---

## ✅ Post-Deploy Verification

### 1. Verificar Lambda

```powershell
aws lambda get-function --function-name orders-api-dev-orders-api
```

✅ **OK si muestra detalles de la función**

### 2. Verificar API Gateway

```powershell
$API_URL = (cd infra; terraform output -raw api_gateway_url)
echo $API_URL
```

✅ **OK si muestra una URL válida**

### 3. Verificar DynamoDB

```powershell
aws dynamodb describe-table --table-name orders-api-dev-orders
```

✅ **OK si muestra la tabla con GSI "CustomerIndex"**

### 4. Verificar Cognito

```powershell
$USER_POOL_ID = (cd infra; terraform output -raw cognito_user_pool_id)
aws cognito-idp describe-user-pool --user-pool-id $USER_POOL_ID
```

✅ **OK si muestra detalles del User Pool**

---

## 🧪 Test Básico

### Crear usuario de prueba

```powershell
$USER_POOL_ID = (cd infra; terraform output -raw cognito_user_pool_id)

aws cognito-idp admin-create-user `
  --user-pool-id $USER_POOL_ID `
  --username test@example.com `
  --user-attributes Name=email,Value=test@example.com `
  --temporary-password "TempPass123!" `
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password `
  --user-pool-id $USER_POOL_ID `
  --username test@example.com `
  --password "TestPass123!" `
  --permanent
```

✅ **OK si no hay errores**

### Obtener token

```powershell
$CLIENT_ID = (cd infra; terraform output -raw cognito_user_pool_client_id)

$TOKEN = aws cognito-idp initiate-auth `
  --auth-flow USER_PASSWORD_AUTH `
  --client-id $CLIENT_ID `
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPass123! `
  --query "AuthenticationResult.IdToken" `
  --output text

echo $TOKEN
```

✅ **OK si muestra un token JWT largo (eyJxxxx...)**

### Test API

```powershell
$API_URL = (cd infra; terraform output -raw api_gateway_url)

# Test con curl
curl -X POST "$API_URL/v1/orders" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{\"customer_id\":\"test-001\",\"total_amount\":99.99,\"status\":\"PENDING\",\"items\":[]}'
```

✅ **OK si devuelve status 201 y un order_id**

**O con PowerShell:**

```powershell
$body = @{
    customer_id = "test-001"
    total_amount = 99.99
    status = "PENDING"
    items = @()
} | ConvertTo-Json

Invoke-RestMethod -Uri "$API_URL/v1/orders" `
  -Method POST `
  -Headers @{
      "Authorization" = "Bearer $TOKEN"
      "Content-Type" = "application/json"
  } `
  -Body $body
```

✅ **OK si devuelve un objeto con order_id**

---

## 🐛 Troubleshooting

### Error: "Error creating Lambda function"

**Causa**: IAM role no creado o permisos insuficientes
**Fix**: Espera 30 segundos y vuelve a hacer `terraform apply`

### Error: "Cognito domain already exists"

**Causa**: El dominio de Cognito debe ser único globalmente
**Fix**: Terraform usa un suffix random automáticamente. Si persiste, ejecuta:
```powershell
cd infra
terraform taint random_string.cognito_domain_suffix
terraform apply
```

### Error: "No authorization token provided"

**Causa**: Falta el header Authorization
**Fix**: Asegúrate de incluir `-H "Authorization: Bearer $TOKEN"`

### Error: "Token has expired"

**Causa**: Los tokens JWT expiran en 1 hora
**Fix**: Obtén un nuevo token con `Get-JWTToken`

### Lambda no se actualiza

**Causa**: Terraform no detecta cambios en el código
**Fix**:
```powershell
cd infra
terraform taint aws_lambda_function.orders_api
terraform apply
```

---

## 📊 Monitoring Post-Deploy

### Ver logs en tiempo real

```powershell
# Lambda logs
aws logs tail /aws/lambda/orders-api-dev-orders-api --follow

# En otra ventana: API Gateway logs
aws logs tail /aws/apigateway/orders-api-dev --follow
```

### Verificar métricas

```powershell
# Ver invocaciones de Lambda
aws cloudwatch get-metric-statistics `
  --namespace AWS/Lambda `
  --metric-name Invocations `
  --dimensions Name=FunctionName,Value=orders-api-dev-orders-api `
  --start-time (Get-Date).AddHours(-1).ToString("yyyy-MM-ddTHH:mm:ss") `
  --end-time (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss") `
  --period 300 `
  --statistics Sum
```

---

## ✅ Success Criteria

Tu deployment es exitoso si:

- ✅ `terraform apply` completa sin errores
- ✅ Outputs muestran URLs e IDs válidos
- ✅ Puedes crear un usuario en Cognito
- ✅ Puedes obtener un token JWT
- ✅ Puedes crear un order via API (POST /v1/orders)
- ✅ Puedes listar orders (GET /v1/orders)
- ✅ Los logs aparecen en CloudWatch

---

## 🎉 Next Steps

Una vez verificado todo:

1. 📖 Lee [API_EXAMPLES.md](API_EXAMPLES.md) para más ejemplos
2. 🧪 Prueba todos los endpoints (GET, POST, PUT, DELETE)
3. 📊 Revisa los logs en CloudWatch
4. 💰 Verifica los costes en AWS Cost Explorer (después de 24h)
5. 🚀 Si todo va bien, considera deployar a prod

---

## 🧹 Cleanup

Cuando termines de probar:

```powershell
cd infra
terraform destroy -var-file="environments\dev.tfvars"
```

**⚠️ Esto eliminará todos los recursos creados**

---

**¡Felicidades! 🎉 Tu API serverless está funcionando en AWS.**
