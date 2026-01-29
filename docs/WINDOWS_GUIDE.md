# 🚀 Quick Start - Windows PowerShell

## Prerequisitos

1. **AWS CLI** instalado y configurado
2. **Terraform** instalado (>= 1.0)
3. **PowerShell 5.1+** (viene con Windows)

### Verificar instalación

```powershell
aws --version
terraform version
$PSVersionTable.PSVersion
```

---

## 🔧 Setup Inicial

### 1. Configurar AWS CLI

```powershell
aws configure
# AWS Access Key ID: [tu-access-key]
# AWS Secret Access Key: [tu-secret-key]
# Default region name: eu-west-1
# Default output format: json
```

### 2. Cargar scripts helper

```powershell
# Desde la raíz del proyecto
. .\scripts.ps1

# Ver comandos disponibles
Show-Help
```

---

## 📦 Deployment

### Desplegar infraestructura (Dev)

```powershell
# 1. Inicializar Terraform
Initialize-Terraform

# 2. Ver plan de deployment
Show-Plan

# 3. Aplicar cambios
Deploy-Infrastructure

# 4. Ver información del deployment
Get-DeploymentInfo
```

### Deployment en una línea

```powershell
cd infra
terraform init
terraform apply -var-file="environments\dev.tfvars"
```

---

## 👤 Crear Usuario

### Con scripts helper

```powershell
# Interactivo
New-CognitoUser
# Email: admin@example.com
# Password: MySecurePass123!
```

### Con AWS CLI directo

```powershell
$USER_POOL_ID = (cd infra; terraform output -raw cognito_user_pool_id)

aws cognito-idp admin-create-user `
  --user-pool-id $USER_POOL_ID `
  --username admin@example.com `
  --user-attributes Name=email,Value=admin@example.com `
  --temporary-password "TempPass123!" `
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password `
  --user-pool-id $USER_POOL_ID `
  --username admin@example.com `
  --password "MySecurePass123!" `
  --permanent
```

---

## 🔐 Obtener Token JWT

### Con scripts helper

```powershell
# Obtener token y guardarlo en variable
$TOKEN = Get-JWTToken
# Email: admin@example.com
# Password: MySecurePass123!

# Ver token
$TOKEN
```

### Con AWS CLI directo

```powershell
$CLIENT_ID = (cd infra; terraform output -raw cognito_user_pool_client_id)

$TOKEN = aws cognito-idp initiate-auth `
  --auth-flow USER_PASSWORD_AUTH `
  --client-id $CLIENT_ID `
  --auth-parameters USERNAME=admin@example.com,PASSWORD=MySecurePass123! `
  --query "AuthenticationResult.IdToken" `
  --output text

echo $TOKEN
```

---

## 🧪 Probar la API

### Test completo automatizado

```powershell
Test-API
# Ejecuta: obtener token → crear order → obtener order → listar orders
```

### Tests individuales

```powershell
# 1. Crear pedido
$ORDER_ID = Test-CreateOrder -Token $TOKEN

# 2. Obtener pedido
Test-GetOrder -OrderId $ORDER_ID -Token $TOKEN

# 3. Listar pedidos
Test-ListOrders -Token $TOKEN
```

### Con cURL manual

```powershell
$API_URL = (cd infra; terraform output -raw api_gateway_url)

# Crear order
curl -X POST "$API_URL/v1/orders" `
  -H "Authorization: Bearer $TOKEN" `
  -H "Content-Type: application/json" `
  -d '{
    \"customer_id\": \"customer-123\",
    \"total_amount\": 99.99,
    \"status\": \"PENDING\",
    \"items\": []
  }'

# Listar orders
curl -X GET "$API_URL/v1/orders" `
  -H "Authorization: Bearer $TOKEN"
```

### Con Invoke-RestMethod (PowerShell nativo)

```powershell
$API_URL = (cd infra; terraform output -raw api_gateway_url)

# Crear order
$body = @{
    customer_id = "customer-123"
    total_amount = 99.99
    status = "PENDING"
    items = @()
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$API_URL/v1/orders" `
  -Method POST `
  -Headers @{
      "Authorization" = "Bearer $TOKEN"
      "Content-Type" = "application/json"
  } `
  -Body $body

$response

# Listar orders
Invoke-RestMethod -Uri "$API_URL/v1/orders" `
  -Method GET `
  -Headers @{ "Authorization" = "Bearer $TOKEN" }
```

---

## 📊 Ver Logs

### Con scripts helper

```powershell
# Logs de Lambda (tiempo real)
Get-LambdaLogs

# Logs de API Gateway
Get-APIGatewayLogs
```

### Con AWS CLI directo

```powershell
$FUNCTION_NAME = (cd infra; terraform output -raw lambda_function_name)

# Logs en tiempo real
aws logs tail "/aws/lambda/$FUNCTION_NAME" --follow

# Últimas 100 líneas
aws logs tail "/aws/lambda/$FUNCTION_NAME" --since 1h

# Buscar errores
aws logs filter-log-events `
  --log-group-name "/aws/lambda/$FUNCTION_NAME" `
  --filter-pattern "ERROR"
```

---

## 🗑️ Limpiar

### Limpiar archivos temporales

```powershell
Clean-Project
```

### Destruir infraestructura

```powershell
# Con script helper (pide confirmación)
Destroy-Infrastructure

# Con Terraform directo
cd infra
terraform destroy -var-file="environments\dev.tfvars"
```

---

## 📋 Comandos Útiles

### Ver información del deployment

```powershell
Get-DeploymentInfo
```

### Ver todos los outputs de Terraform

```powershell
Get-Outputs
```

### Ver recursos en AWS

```powershell
# Lambda functions
aws lambda list-functions --query "Functions[?contains(FunctionName, 'orders-api')]"

# DynamoDB tables
aws dynamodb list-tables --query "TableNames[?contains(@, 'orders')]"

# API Gateways
aws apigateway get-rest-apis --query "items[?contains(name, 'orders-api')]"
```

---

## 🔄 Workflow Completo

```powershell
# 1. Setup inicial (solo una vez)
. .\scripts.ps1
Initialize-Terraform

# 2. Deploy
Deploy-Infrastructure

# 3. Configurar usuario
New-CognitoUser

# 4. Obtener token
$TOKEN = Get-JWTToken

# 5. Probar API
Test-API

# 6. Ver logs (en otra ventana)
Get-LambdaLogs

# 7. Cuando termines
Destroy-Infrastructure
```

---

## 💡 Tips

### Guardar variables en sesión

```powershell
# Al inicio de tu sesión
$API_URL = (cd infra; terraform output -raw api_gateway_url)
$USER_POOL_ID = (cd infra; terraform output -raw cognito_user_pool_id)
$CLIENT_ID = (cd infra; terraform output -raw cognito_user_pool_client_id)
$TOKEN = Get-JWTToken

# Usar durante la sesión
Invoke-RestMethod -Uri "$API_URL/v1/orders" -Method GET `
  -Headers @{ "Authorization" = "Bearer $TOKEN" }
```

### Alias útiles

```powershell
# Agregar a tu perfil de PowerShell ($PROFILE)
function deploy { Deploy-Infrastructure }
function logs { Get-LambdaLogs }
function token { Get-JWTToken }
```

### Ver perfil de PowerShell

```powershell
# Ver ubicación del perfil
$PROFILE

# Editar perfil
notepad $PROFILE

# Agregar al perfil
Set-Location "C:\Users\vdiaz2\Documents\orders-serveless-api"
. .\scripts.ps1
```

---

## 🐛 Troubleshooting

### Error: "Unable to locate credentials"

```powershell
aws configure
# Verifica que tengas credenciales configuradas
```

### Error: "Token has expired"

```powershell
# Los tokens JWT expiran en 1 hora, obtén uno nuevo
$TOKEN = Get-JWTToken
```

### Error: Terraform state locked

```powershell
# Si el apply se interrumpió
cd infra
terraform force-unlock <LOCK_ID>
```

### Ver estado de recursos

```powershell
cd infra
terraform show
terraform state list
```

---

## 📚 Recursos

- [AWS CLI Reference](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [API Gateway REST API](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-rest-api.html)
- [Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

---

**Stack**: Python 3.11 | Terraform | Lambda | API Gateway | DynamoDB | Cognito
