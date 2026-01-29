# Orders API - PowerShell Helper Scripts
# Para usuarios de Windows

# Variables globales
$REGION = "eu-west-1"
$ENV = "dev"

function Show-Help {
    Write-Host "`n📦 Orders Serverless API - Helper Commands`n" -ForegroundColor Cyan
    Write-Host "Deployment:" -ForegroundColor Yellow
    Write-Host "  Initialize-Terraform       Inicializar Terraform"
    Write-Host "  Show-Plan                  Ver plan de deployment"
    Write-Host "  Deploy-Infrastructure      Desplegar infraestructura"
    Write-Host "  Destroy-Infrastructure     Destruir infraestructura`n"

    Write-Host "Cognito:" -ForegroundColor Yellow
    Write-Host "  New-CognitoUser            Crear usuario de prueba"
    Write-Host "  Get-JWTToken               Obtener token JWT`n"

    Write-Host "Testing:" -ForegroundColor Yellow
    Write-Host "  Test-API                   Test rápido de la API"
    Write-Host "  Test-CreateOrder           Crear pedido de prueba`n"

    Write-Host "Logs:" -ForegroundColor Yellow
    Write-Host "  Get-LambdaLogs             Ver logs de Lambda"
    Write-Host "  Get-APIGatewayLogs         Ver logs de API Gateway`n"

    Write-Host "Info:" -ForegroundColor Yellow
    Write-Host "  Get-DeploymentInfo         Mostrar info del deployment"
    Write-Host "  Get-Outputs                Ver outputs de Terraform`n"
}

function Initialize-Terraform {
    Write-Host "🔧 Inicializando Terraform..." -ForegroundColor Green
    Push-Location infra
    terraform init
    Pop-Location
}

function Show-Plan {
    param([string]$Environment = "dev")
    Write-Host "📋 Planificando deployment para $Environment..." -ForegroundColor Green
    Push-Location infra
    terraform plan -var-file="environments/$Environment.tfvars"
    Pop-Location
}

function Deploy-Infrastructure {
    param([string]$Environment = "dev")
    Write-Host "🚀 Desplegando infraestructura en $Environment..." -ForegroundColor Green
    Push-Location infra
    terraform apply -var-file="environments/$Environment.tfvars"
    Pop-Location
}

function Destroy-Infrastructure {
    param([string]$Environment = "dev")
    Write-Host "⚠️  ¡VAS A DESTRUIR LA INFRAESTRUCTURA DE $Environment!" -ForegroundColor Red
    $confirmation = Read-Host "¿Estás seguro? (escribe 'yes' para confirmar)"

    if ($confirmation -eq "yes") {
        Push-Location infra
        terraform destroy -var-file="environments/$Environment.tfvars"
        Pop-Location
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function Get-Outputs {
    Write-Host "📊 Outputs de Terraform:" -ForegroundColor Cyan
    Push-Location infra
    terraform output
    Pop-Location
}

function Get-DeploymentInfo {
    Write-Host "`n📌 Información del deployment:" -ForegroundColor Cyan
    Push-Location infra

    $apiUrl = terraform output -raw api_gateway_url
    $userPoolId = terraform output -raw cognito_user_pool_id
    $clientId = terraform output -raw cognito_user_pool_client_id
    $tableName = terraform output -raw dynamodb_table_name

    Write-Host "`nAPI Gateway URL:" -ForegroundColor Yellow
    Write-Host "  $apiUrl" -ForegroundColor White

    Write-Host "`nCognito User Pool ID:" -ForegroundColor Yellow
    Write-Host "  $userPoolId" -ForegroundColor White

    Write-Host "`nCognito Client ID:" -ForegroundColor Yellow
    Write-Host "  $clientId" -ForegroundColor White

    Write-Host "`nDynamoDB Table:" -ForegroundColor Yellow
    Write-Host "  $tableName" -ForegroundColor White

    Pop-Location
}

function New-CognitoUser {
    Write-Host "👤 Crear nuevo usuario en Cognito`n" -ForegroundColor Cyan

    $email = Read-Host "Email"
    $password = Read-Host "Password" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )

    Push-Location infra
    $userPoolId = terraform output -raw cognito_user_pool_id
    Pop-Location

    Write-Host "`nCreando usuario..." -ForegroundColor Green

    aws cognito-idp admin-create-user `
        --user-pool-id $userPoolId `
        --username $email `
        --user-attributes Name=email,Value=$email `
        --temporary-password "TempPass123!" `
        --message-action SUPPRESS `
        --region $REGION

    aws cognito-idp admin-set-user-password `
        --user-pool-id $userPoolId `
        --username $email `
        --password $passwordPlain `
        --permanent `
        --region $REGION

    Write-Host "✅ Usuario creado: $email" -ForegroundColor Green
}

function Get-JWTToken {
    Write-Host "🔐 Obtener token JWT`n" -ForegroundColor Cyan

    $email = Read-Host "Email"
    $password = Read-Host "Password" -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )

    Push-Location infra
    $clientId = terraform output -raw cognito_user_pool_client_id
    Pop-Location

    Write-Host "`nObteniendo token..." -ForegroundColor Green

    $token = aws cognito-idp initiate-auth `
        --auth-flow USER_PASSWORD_AUTH `
        --client-id $clientId `
        --auth-parameters USERNAME=$email,PASSWORD=$passwordPlain `
        --region $REGION `
        --query 'AuthenticationResult.IdToken' `
        --output text

    Write-Host "`n✅ Token JWT:" -ForegroundColor Green
    Write-Host $token -ForegroundColor Yellow
    Write-Host "`n💡 Guarda este token en una variable:" -ForegroundColor Cyan
    Write-Host "`$TOKEN = '$token'" -ForegroundColor White

    return $token
}

function Test-CreateOrder {
    param([string]$Token)

    if (-not $Token) {
        $Token = Read-Host "Token JWT"
    }

    Push-Location infra
    $apiUrl = terraform output -raw api_gateway_url
    Pop-Location

    $body = @{
        customer_id = "test-customer-001"
        total_amount = 99.99
        status = "PENDING"
        items = @(
            @{
                product_id = "prod-001"
                name = "Test Product"
                quantity = 1
                price = 99.99
            }
        )
    } | ConvertTo-Json

    Write-Host "`n🧪 Creando pedido de prueba..." -ForegroundColor Cyan

    $response = Invoke-RestMethod -Uri "$apiUrl/v1/orders" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $Token"
            "Content-Type" = "application/json"
        } `
        -Body $body

    Write-Host "`n✅ Pedido creado:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10

    return $response.order_id
}

function Test-GetOrder {
    param(
        [string]$OrderId,
        [string]$Token
    )

    if (-not $Token) {
        $Token = Read-Host "Token JWT"
    }

    if (-not $OrderId) {
        $OrderId = Read-Host "Order ID"
    }

    Push-Location infra
    $apiUrl = terraform output -raw api_gateway_url
    Pop-Location

    Write-Host "`n🔍 Obteniendo pedido $OrderId..." -ForegroundColor Cyan

    $response = Invoke-RestMethod -Uri "$apiUrl/v1/orders/$OrderId" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $Token"
        }

    Write-Host "`n✅ Pedido encontrado:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
}

function Test-ListOrders {
    param([string]$Token)

    if (-not $Token) {
        $Token = Read-Host "Token JWT"
    }

    Push-Location infra
    $apiUrl = terraform output -raw api_gateway_url
    Pop-Location

    Write-Host "`n📋 Listando pedidos..." -ForegroundColor Cyan

    $response = Invoke-RestMethod -Uri "$apiUrl/v1/orders" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $Token"
        }

    Write-Host "`n✅ Pedidos encontrados: $($response.count)" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
}

function Get-LambdaLogs {
    Push-Location infra
    $functionName = terraform output -raw lambda_function_name
    Pop-Location

    Write-Host "`n📊 Mostrando logs de Lambda ($functionName)..." -ForegroundColor Cyan
    Write-Host "Presiona Ctrl+C para salir`n" -ForegroundColor Yellow

    aws logs tail "/aws/lambda/$functionName" --follow --region $REGION
}

function Get-APIGatewayLogs {
    param([string]$Environment = "dev")

    Write-Host "`n📊 Mostrando logs de API Gateway..." -ForegroundColor Cyan
    Write-Host "Presiona Ctrl+C para salir`n" -ForegroundColor Yellow

    aws logs tail "/aws/apigateway/orders-api-$Environment" --follow --region $REGION
}

function Test-API {
    Write-Host "`n🧪 Test Completo de la API`n" -ForegroundColor Cyan

    # 1. Obtener token
    Write-Host "1️⃣ Obteniendo token JWT..." -ForegroundColor Yellow
    $token = Get-JWTToken

    if (-not $token) {
        Write-Host "❌ No se pudo obtener el token" -ForegroundColor Red
        return
    }

    # 2. Crear pedido
    Write-Host "`n2️⃣ Creando pedido..." -ForegroundColor Yellow
    $orderId = Test-CreateOrder -Token $token

    # 3. Obtener pedido
    Write-Host "`n3️⃣ Obteniendo pedido..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Test-GetOrder -OrderId $orderId -Token $token

    # 4. Listar pedidos
    Write-Host "`n4️⃣ Listando pedidos..." -ForegroundColor Yellow
    Test-ListOrders -Token $token

    Write-Host "`n✅ Test completado!" -ForegroundColor Green
}

function Format-Code {
    Write-Host "🎨 Formateando código Python..." -ForegroundColor Cyan

    if (Get-Command black -ErrorAction SilentlyContinue) {
        black src/orders/*.py
    } else {
        Write-Host "⚠️  'black' no está instalado. Instálalo con: pip install black" -ForegroundColor Yellow
    }

    if (Get-Command isort -ErrorAction SilentlyContinue) {
        isort src/orders/*.py
    } else {
        Write-Host "⚠️  'isort' no está instalado. Instálalo con: pip install isort" -ForegroundColor Yellow
    }
}

function Clean-Project {
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Cyan

    # Python cache
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" | Remove-Item -Force

    # Terraform
    if (Test-Path "infra\.terraform.lock.hcl") {
        Remove-Item "infra\.terraform.lock.hcl" -Force
    }
    if (Test-Path "infra\lambda_function.zip") {
        Remove-Item "infra\lambda_function.zip" -Force
    }

    Write-Host "✅ Limpieza completada" -ForegroundColor Green
}

# Exportar funciones
Export-ModuleMember -Function *

# Mostrar ayuda al cargar
Write-Host "`n📦 Orders Serverless API - PowerShell Helper" -ForegroundColor Cyan
Write-Host "Ejecuta 'Show-Help' para ver todos los comandos disponibles`n" -ForegroundColor White
