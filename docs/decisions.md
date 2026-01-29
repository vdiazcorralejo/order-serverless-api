# Decisiones Arquitectónicas

## Contexto

API serverless para gestión de pedidos (Orders API) diseñada para demostrar conocimientos en arquitectura cloud, serverless y mejores prácticas de AWS.

---

## Decisión 1: Arquitectura Serverless

### Opciones consideradas
- Serverless (Lambda + API Gateway)
- Contenedores (ECS/Fargate)
- EC2 tradicional

### Decisión
✅ **Serverless con Lambda + API Gateway**

### Razones
- **Zero gestión de servidores**: No hay que mantener OS, parches, scaling
- **Pay-per-use**: Sólo pagas por requests reales
- **Auto-scaling**: Maneja de 1 a miles de requests sin configuración
- **Time-to-market**: Deploy rápido, ideal para MVP
- **Coste inicial bajo**: Perfecto para proyectos que empiezan

### Consecuencias
- ✅ Coste muy bajo para tráfico bajo
- ✅ Escalabilidad automática
- ✅ Alta disponibilidad por defecto
- ⚠️ Cold starts (mitigable con provisioned concurrency)
- ⚠️ Timeout máximo 15 min (no aplica aquí)

---

## Decisión 2: Python como lenguaje

### Opciones consideradas
- Python
- Node.js
- Java
- Go

### Decisión
✅ **Python 3.11**

### Razones
- **boto3 nativo**: SDK oficial de AWS, excelente documentación
- **Rápido desarrollo**: Sintaxis clara, menos código boilerplate
- **Muy usado en serverless**: Gran ecosistema de librerías
- **Perfil profesional**: Encaja con datos y automatización

### Consecuencias
- ✅ Desarrollo ágil
- ✅ Código legible y mantenible
- ✅ Gran ecosistema
- ⚠️ Arranque ligeramente más lento que Go (aceptable)

---

## Decisión 3: Terraform para IaC

### Opciones consideradas
- Terraform
- AWS CDK
- CloudFormation
- Serverless Framework

### Decisión
✅ **Terraform**

### Razones
- **Más demandado en empresas**: Mayor empleabilidad
- **Multi-cloud**: No te ata a AWS (aunque aquí usamos AWS)
- **Declarativo**: Más predecible que imperativo
- **State management**: Control explícito del estado
- **HCL**: Lenguaje específico, más estándar que CDK

### Consecuencias
- ✅ Habilidad muy valorada en el mercado
- ✅ Infraestructura reproducible
- ✅ GitOps friendly
- ⚠️ Curva de aprendizaje inicial (asumible)

---

## Decisión 4: DynamoDB como base de datos

### Opciones consideradas
- DynamoDB
- RDS (PostgreSQL/MySQL)
- Aurora Serverless

### Decisión
✅ **DynamoDB (on-demand)**

### Razones
- **Zero mantenimiento**: No hay instancias, backups automáticos
- **Perfecto para serverless**: Scale to zero real
- **Performance predecible**: Latencia < 10ms
- **Pay-per-request**: Ideal para tráfico variable
- **Modelo de datos simple**: Key-value + GSI suficiente para orders

### Consecuencias
- ✅ Coste muy bajo para tráfico bajo
- ✅ No hay que gestionar conexiones
- ✅ Escala automática
- ⚠️ Queries limitados (solucionado con GSI)
- ⚠️ No soporta joins (no necesario aquí)

**Diseño de tabla:**
- PK: `order_id` (uuid)
- GSI: `customer_id` + `created_at` (para queries por cliente)

---

## Decisión 5: Cognito para autenticación

### Opciones consideradas
- Cognito User Pools
- Auth0
- Custom JWT
- API Keys

### Decisión
✅ **AWS Cognito User Pools + JWT Authorizer**

### Razones
- **Integración nativa**: API Gateway tiene authorizer built-in
- **Sin código de auth**: No hay que implementar login/signup
- **JWT estándar**: Tokens seguros y verificables
- **Gestión de usuarios**: Console + CLI para crear users
- **Gratis hasta 50K MAU**: Perfecto para este caso

### Consecuencias
- ✅ Seguridad robusta sin código custom
- ✅ Menos superficie de ataque
- ✅ Tokens con expiración automática
- ⚠️ Vendor lock-in (aceptable para AWS)

---

## Decisión 6: Versionado de API (/v1)

### Opciones consideradas
- `/v1/orders`
- `/orders` (sin versión)
- Header-based versioning

### Decisión
✅ **Path-based versioning: `/v1/orders`**

### Razones
- **Explícito**: El cliente sabe qué versión usa
- **Fácil routing**: API Gateway puede routear por path
- **Estándar REST**: Muy común en APIs públicas
- **Deprecación gradual**: Puedes mantener v1 y v2 en paralelo

### Consecuencias
- ✅ Evolución sin romper clientes
- ✅ Fácil de documentar
- ✅ Clear contract

---

## Decisión 7: Arquitectura limpia en Lambda

### Estructura
```
handler.py       → HTTP routing + validation
models.py        → Domain models
repository.py    → Data access layer
```

### Razones
- **Separation of concerns**: Cada archivo una responsabilidad
- **Testeable**: Se pueden hacer unit tests fácilmente
- **Mantenible**: Fácil de entender y modificar
- **Escalable**: Se pueden agregar más modelos/repos

### Consecuencias
- ✅ Código profesional
- ✅ Fácil de extender
- ✅ Buenas prácticas demostradas

---

## Decisión 8: CloudWatch para observabilidad

### Opciones consideradas
- CloudWatch Logs + Metrics
- Datadog
- New Relic
- Elastic Stack

### Decisión
✅ **CloudWatch (nativo)**

### Razones
- **Integración nativa**: Lambda y API Gateway loggean automáticamente
- **Coste incluido**: Hasta 5GB gratis al mes
- **Suficiente para MVP**: Logs, metrics, alarmas básicas
- **No requiere configuración extra**: Funciona out-of-the-box

### Consecuencias
- ✅ Setup inmediato
- ✅ Coste bajo
- ⚠️ UI menos amigable que alternativas (aceptable)

---

## Decisión 9: Separación de entornos (dev/prod)

### Estructura
```
environments/
  dev.tfvars
  prod.tfvars
```

### Razones
- **Best practice estándar**: Nunca probar en producción
- **Configuración diferenciada**: Rate limits, logs retention, etc.
- **Coste optimizado**: Dev con menos recursos
- **Seguridad**: prod con PITR, encryption, alarmas

### Consecuencias
- ✅ Deploy seguro
- ✅ Testing sin afectar prod
- ✅ Costes controlados

---

## Decisión 10: Rate limiting + Usage Plans

### Configuración
- Dev: 50 req/s burst 100
- Prod: 250 req/s burst 500

### Razones
- **Protección contra abuso**: Evita que un cliente sature la API
- **Coste controlado**: Limita invocaciones no esperadas
- **SLA claro**: El cliente sabe sus límites
- **Escalable**: Se puede aumentar con usage plans

### Consecuencias
- ✅ API protegida
- ✅ Costes predecibles
- ✅ Comportamiento profesional

---

## Trade-offs aceptados

1. **No hay tests automatizados**: Para acelerar desarrollo inicial (agregar después)
2. **Scan en list_orders sin filtro**: Usar con caución en prod (agregar pagination)
3. **No hay caché**: Añadir ElastiCache si se necesita más adelante
4. **No hay CI/CD**: Deployar manualmente con Terraform (GitHub Actions después)

---

## Métricas de éxito del diseño

- ✅ Deploy en < 10 minutos con `terraform apply`
- ✅ Coste mensual < 10€ para tráfico bajo
- ✅ Latencia p95 < 500ms
- ✅ Código Python < 300 líneas
- ✅ 100% serverless (cero EC2)

---

**Última actualización**: 2026-01-29
