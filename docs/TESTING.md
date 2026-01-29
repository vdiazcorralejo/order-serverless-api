# Testing Guide - Orders Serverless API

## 📋 Tabla de Contenidos

- [Estructura de Tests](#estructura-de-tests)
- [Instalación](#instalación)
- [Ejecutar Tests](#ejecutar-tests)
- [Tipos de Tests](#tipos-de-tests)
- [Coverage](#coverage)
- [CI/CD](#cicd)
- [Best Practices](#best-practices)

---

## 🏗️ Estructura de Tests

```
tests/
├── unit/                      # Tests unitarios (rápidos, sin AWS)
│   ├── test_models.py        # Tests de Order, OrderItem, OrderStatus
│   ├── test_repository.py    # Tests de OrderRepository (mock DynamoDB)
│   └── test_handler.py       # Tests de Lambda handler (mock repository)
├── integration/               # Tests de integración (con AWS mocked o real)
│   └── test_api_endpoints.py # Tests E2E de API endpoints
├── conftest.py               # Fixtures compartidas (pytest)
└── requirements.txt          # Dependencias de tests
```

**Total**: 4 archivos de tests con ~50+ test cases

---

## 📦 Instalación

### Instalar dependencias de tests

```bash
# Desde la raíz del proyecto
pip install -r tests/requirements.txt
```

### Instalar pre-commit hooks (opcional)

```bash
pip install pre-commit
pre-commit install
```

---

## 🚀 Ejecutar Tests

### Todos los tests

```bash
pytest
```

### Solo tests unitarios (rápido)

```bash
pytest tests/unit/
```

### Solo tests de integración

```bash
pytest tests/integration/
```

### Test específico

```bash
pytest tests/unit/test_models.py::TestOrder::test_order_creation_valid
```

### Con cobertura

```bash
pytest --cov=src/orders --cov-report=html
```

Luego abre `coverage_html/index.html` en tu navegador.

### Modo verbose

```bash
pytest -v
```

### Modo watch (re-run on changes)

```bash
pip install pytest-watch
pytest-watch
```

---

## 🧪 Tipos de Tests

### 1. Unit Tests (`tests/unit/`)

**Características:**
- ⚡ Rápidos (< 1 segundo total)
- 🔌 Sin dependencias externas
- 🎭 Mock de AWS services

**Archivos:**

#### `test_models.py`
Tests de modelos de dominio sin AWS.

```bash
pytest tests/unit/test_models.py -v
```

**Test cases:**
- ✅ `test_order_creation_valid` - Crear orden válida
- ✅ `test_order_negative_amount_fails` - Validar monto negativo falla
- ✅ `test_order_invalid_status_fails` - Status inválido falla
- ✅ `test_order_to_dict` - Serialización
- ✅ `test_order_from_dict` - Deserialización
- ✅ Y más...

#### `test_repository.py`
Tests de capa de datos con DynamoDB mockeado (moto).

```bash
pytest tests/unit/test_repository.py -v
```

**Test cases:**
- ✅ `test_create_order_success` - Crear orden
- ✅ `test_get_order_found` - Obtener orden existente
- ✅ `test_get_order_not_found` - Orden no existe
- ✅ `test_update_order_success` - Actualizar orden
- ✅ `test_delete_order_success` - Eliminar orden
- ✅ `test_list_orders` - Listar todas
- ✅ `test_get_orders_by_customer` - Filtrar por customer

#### `test_handler.py`
Tests de Lambda handler con repository mockeado.

```bash
pytest tests/unit/test_handler.py -v
```

**Test cases:**
- ✅ `test_post_orders_valid` - POST /v1/orders
- ✅ `test_get_orders_list` - GET /v1/orders
- ✅ `test_get_order_by_id_found` - GET /v1/orders/{id}
- ✅ `test_put_order_success` - PUT /v1/orders/{id}
- ✅ `test_delete_order_success` - DELETE /v1/orders/{id}
- ✅ `test_invalid_http_method` - Método no soportado
- ✅ `test_missing_authorization` - Sin auth

---

### 2. Integration Tests (`tests/integration/`)

**Características:**
- 🌐 Tests E2E con API real
- 🔐 Requiere autenticación (ID_TOKEN)
- ⏱️ Más lentos (varios segundos)

#### `test_api_endpoints.py`
Tests completos contra API desplegada.

**Setup:**
```bash
# Set environment variables
export API_URL="https://your-api-gateway-url.amazonaws.com/dev"
export ID_TOKEN="your-cognito-id-token"

# Run integration tests
pytest tests/integration/ -v
```

**Windows:**
```cmd
set API_URL=https://your-api-gateway-url.amazonaws.com/dev
set ID_TOKEN=your-cognito-id-token
pytest tests/integration/ -v
```

**Test cases:**
- ✅ `test_create_order_e2e` - Crear orden E2E
- ✅ `test_list_orders_e2e` - Listar órdenes E2E
- ✅ `test_get_order_e2e` - Obtener orden E2E
- ✅ `test_update_order_e2e` - Actualizar orden E2E
- ✅ `test_delete_order_e2e` - Eliminar orden E2E
- ✅ `test_authentication_required` - Auth requerida
- ✅ `test_invalid_token_rejected` - Token inválido rechazado
- ✅ `test_response_time` - Performance test
- ✅ `test_concurrent_requests` - Concurrencia

---

## 📊 Coverage

### Generar reporte de cobertura

```bash
pytest --cov=src/orders --cov-report=html --cov-report=term-missing
```

### Ver reporte HTML

```bash
# El reporte se genera en coverage_html/
open coverage_html/index.html  # Mac/Linux
start coverage_html/index.html # Windows
```

### Coverage objetivo

- **Unit tests**: >80% coverage
- **Integration tests**: Happy paths + error cases principales

### Archivos de configuración

**pytest.ini**
```ini
[pytest]
addopts =
    --cov=src/orders
    --cov-report=html
    --cov-report=term-missing
```

**.coveragerc**
```ini
[run]
source = src/orders
omit = */tests/*
```

---

## 🔄 CI/CD

### GitHub Actions

El proyecto incluye CI/CD automático en `.github/workflows/tests.yml`.

**Se ejecuta en:**
- ✅ Push a `main` o `develop`
- ✅ Pull requests
- ✅ Manual (workflow_dispatch)

**Jobs incluidos:**

1. **unit-tests** - Tests unitarios con coverage
2. **integration-tests** - Tests de integración (mockeados)
3. **lint** - Linting con flake8, black, isort
4. **security** - Scan con bandit y safety
5. **test-summary** - Resumen de resultados

**Ver resultados:**
- Ve a GitHub → Actions tab
- Cada push/PR muestra resultados

### Pre-commit Hooks

Ejecuta checks antes de cada commit.

**Instalar:**
```bash
pip install pre-commit
pre-commit install
```

**Hooks incluidos:**
- ✅ Black (formatting)
- ✅ isort (import sorting)
- ✅ flake8 (linting)
- ✅ bandit (security)
- ✅ Terraform fmt
- ✅ YAML/JSON validation

**Ejecutar manualmente:**
```bash
pre-commit run --all-files
```

---

## 💡 Best Practices

### 1. Escribir tests primero (TDD)

```python
# 1. Escribir test que falla
def test_new_feature():
    result = new_feature()
    assert result == expected

# 2. Implementar feature
def new_feature():
    return expected

# 3. Refactorizar
```

### 2. Tests deben ser FIRST

- **F**ast - Rápidos (< 1s para unit tests)
- **I**ndependent - Independientes entre sí
- **R**epeatable - Mismo resultado cada vez
- **S**elf-validating - Pass/fail claro
- **T**imely - Escritos a tiempo (antes o con el código)

### 3. Naming conventions

```python
# ✅ BUENO: Nombres descriptivos
def test_order_creation_with_negative_amount_raises_error():
    ...

# ❌ MALO: Nombres genéricos
def test_1():
    ...
```

### 4. Arrange-Act-Assert (AAA)

```python
def test_create_order():
    # Arrange - Setup
    order_data = {...}

    # Act - Execute
    result = create_order(order_data)

    # Assert - Verify
    assert result.status == "PENDING"
```

### 5. Un assert por test (cuando sea posible)

```python
# ✅ BUENO: Foco claro
def test_order_has_id():
    order = Order(...)
    assert order.order_id is not None

def test_order_has_correct_status():
    order = Order(...)
    assert order.status == OrderStatus.PENDING

# ⚠️ ACEPTABLE: Asserts relacionados
def test_order_serialization():
    order = Order(...)
    data = order.to_dict()
    assert 'order_id' in data
    assert 'status' in data
```

### 6. Mock dependencias externas

```python
# ✅ BUENO: Mock AWS
@mock_dynamodb
def test_repository():
    ...

# ✅ BUENO: Mock repository
@patch('handler.OrderRepository')
def test_handler(mock_repo):
    ...
```

---

## 🐛 Debugging Tests

### Ver print statements

```bash
pytest -s
```

### Debugger interactivo

```bash
pytest --pdb
```

### Ver variables locales en fallos

```bash
pytest -l
```

### Solo tests que fallaron antes

```bash
pytest --lf
```

---

## 📈 Métricas de Tests

### Resumen actual

| Métrica | Valor |
|---------|-------|
| Total tests | 50+ |
| Unit tests | 40+ |
| Integration tests | 10+ |
| Coverage | ~80-85% |
| Tiempo unit | < 5 segundos |
| Tiempo integration | ~30 segundos |

---

## 🔧 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'orders'`

**Solución:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
# o
pip install -e .
```

### Error: `AWS credentials not found`

**Solución (tests unitarios):**
```bash
# Moto mock automáticamente, pero asegúrate de:
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
```

### Error: `API_URL or ID_TOKEN not set`

**Solución (tests integración):**
```bash
export API_URL="https://your-api.execute-api.eu-west-1.amazonaws.com/dev"
export ID_TOKEN=$(aws cognito-idp admin-initiate-auth ...)
```

### Tests muy lentos

**Solución:**
```bash
# Solo unit tests
pytest tests/unit/

# Tests en paralelo
pytest -n auto
```

---

## 📚 Recursos Adicionales

- [Pytest Documentation](https://docs.pytest.org/)
- [Moto (AWS mocking)](https://github.com/getmoto/moto)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)

---

## ✅ Checklist de Tests

Antes de hacer commit:

- [ ] Todos los tests pasan (`pytest`)
- [ ] Coverage > 80% (`pytest --cov`)
- [ ] No hay warnings
- [ ] Pre-commit hooks pasan
- [ ] Tests nuevos para features nuevas
- [ ] Tests actualizados para cambios

---

## 🎯 Próximos Pasos

1. **Ejecutar tests localmente:**
   ```bash
   pip install -r tests/requirements.txt
   pytest
   ```

2. **Ver coverage:**
   ```bash
   pytest --cov=src/orders --cov-report=html
   open coverage_html/index.html
   ```

3. **Instalar pre-commit:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Push a GitHub** - CI/CD se ejecuta automáticamente

---

**Happy Testing! 🧪✨**
