# Sistema de Procesamiento de Órdenes Distribuido

## 🏗️ Arquitectura del Sistema

Este es un sistema de microservicios basado en **Event-Driven Architecture** y **Saga Pattern** para el procesamiento distribuido de órdenes.

### Microservicios

1. **Order Service** (Puerto 8001)
   - Gestión de órdenes
   - Publica: `OrderCreated`, `OrderCancelled`
   - Se suscribe: `PaymentProcessed`, `PaymentFailed`

2. **Inventory Service** (Puerto 8002)
   - Gestión de inventario
   - Se suscribe: `OrderCreated`
   - Publica: `InventoryReserved`, `InventoryUnavailable`

3. **Payment Service** (Puerto 8003)
   - Procesamiento de pagos con retry logic
   - Se suscribe: `InventoryReserved`
   - Publica: `PaymentProcessed`, `PaymentFailed`
   - **Retry Logic**: 3 intentos con exponential backoff (1s, 2s, 4s)
   - **Tasa de éxito**: 80% simulada

4. **Notification Service** (Puerto 8004)
   - Servicio stateless de notificaciones
   - Se suscribe: `OrderConfirmed`, `PaymentProcessed`, `PaymentFailed`, `OrderCompleted`

### Infraestructura

- **PostgreSQL**: Base de datos compartida para Order, Inventory y Payment services
- **RabbitMQ**: Message broker para comunicación asíncrona
- **Docker Compose**: Orquestación de todos los servicios

## 🔄 Flujo de Eventos (Saga Pattern)

```mermaid
sequenceDiagram
    participant Client
    participant OrderService
    participant InventoryService
    participant PaymentService
    participant NotificationService
    participant RabbitMQ

    Client->>OrderService: POST /orders
    OrderService->>RabbitMQ: OrderCreated
    RabbitMQ->>InventoryService: OrderCreated
    
    alt Inventory Available
        InventoryService->>RabbitMQ: InventoryReserved
        RabbitMQ->>PaymentService: InventoryReserved
        
        alt Payment Success (80% rate)
            PaymentService->>RabbitMQ: PaymentProcessed
            RabbitMQ->>OrderService: PaymentProcessed
            RabbitMQ->>NotificationService: PaymentProcessed
            OrderService->>Client: Order Completed
        else Payment Failed (with retry)
            PaymentService->>RabbitMQ: PaymentFailed
            RabbitMQ->>OrderService: PaymentFailed
            RabbitMQ->>NotificationService: PaymentFailed
            OrderService->>Client: Order Failed
        end
    else Inventory Unavailable
        InventoryService->>RabbitMQ: InventoryUnavailable
        RabbitMQ->>NotificationService: InventoryUnavailable
        OrderService->>Client: Order Failed
    end
```

## 🛠️ Stack Tecnológico

- **Python 3.11+**
- **FastAPI** (async/await)
- **PostgreSQL** con `asyncpg`
- **SQLAlchemy** (async)
- **RabbitMQ** con `aio-pika`
- **Alembic** (migraciones automáticas)
- **Pydantic** (validación y serialización)
- **Poetry** (gestión de dependencias)
- **Docker & Docker Compose**
- **pytest-asyncio** (testing)

## 🚀 Instrucciones de Setup

### Prerrequisitos

- Docker y Docker Compose instalados
- Python 3.11+ (para desarrollo local)
- Poetry (para gestión de dependencias)

### Ejecución Completa

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd order-processing-system
```

2. **Iniciar todos los servicios**
```bash
docker-compose up --build
```

Este comando:
- Construye las imágenes de los 4 microservicios
- Inicia PostgreSQL y RabbitMQ
- Ejecuta migraciones automáticamente
- Inicia todos los servicios con health checks

### Verificación del Sistema

Una vez iniciado, los servicios estarán disponibles en:

- **Order Service**: http://localhost:8001
- **Inventory Service**: http://localhost:8002  
- **Payment Service**: http://localhost:8003
- **Notification Service**: http://localhost:8004
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

### Health Checks

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## 📋 API Endpoints

### Order Service

```bash
# Crear orden
POST http://localhost:8001/orders
{
  "customer_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "price": 10.0
    }
  ]
}

# Obtener orden
GET http://localhost:8001/orders/{order_id}

# Cancelar orden
DELETE http://localhost:8001/orders/{order_id}

# Listar órdenes de cliente
GET http://localhost:8001/orders/customer/{customer_id}
```

### Inventory Service

```bash
# Obtener inventario
GET http://localhost:8002/inventory/{product_id}

# Actualizar inventario
PUT http://localhost:8002/inventory/{product_id}
{
  "quantity_available": 100
}
```

### Payment Service

```bash
# Obtener pago
GET http://localhost:8003/payments/{payment_id}

# Obtener pago por orden
GET http://localhost:8003/payments/order/{order_id}
```

### Notification Service

```bash
# Enviar notificación personalizada
POST http://localhost:8004/notifications
{
  "customer_id": "uuid",
  "subject": "Test",
  "message": "Test message"
}
```

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Order Service
cd order-service
poetry install
poetry run pytest

# Inventory Service
cd inventory-service
poetry install
poetry run pytest

# Payment Service
cd payment-service
poetry install
poetry run pytest

# Notification Service
cd notification-service
poetry install
poetry run pytest
```

### Tests Incluidos

- **Order Service**: 3 tests unitarios con mocking de RabbitMQ y PostgreSQL
- **Inventory Service**: Tests de reserva de inventario
- **Payment Service**: Tests de retry logic y exponential backoff
- **Notification Service**: Tests de envío de notificaciones

## 🏛️ Arquitectura de Capas (Clean Architecture)

Cada microservicio sigue la estructura de Clean Architecture:

```
service/
├── api/           # FastAPI routes y controllers
├── application/   # Use cases y lógica de negocio
├── domain/        # Modelos y eventos de dominio
├── infrastructure/# Repositorios, DB, Message Queue
├── tests/         # Tests unitarios
├── alembic/       # Migraciones de DB (excepto notification)
├── Dockerfile
└── pyproject.toml
```

## 🔧 Desarrollo Local

### Setup de Desarrollo

1. **Instalar dependencias por servicio**
```bash
cd order-service
poetry install
```

2. **Variables de entorno**
```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/order_processing"
export RABBITMQ_URL="amqp://admin:admin@localhost:5672/"
```

3. **Ejecutar migraciones**
```bash
alembic upgrade head
```

4. **Iniciar servicio**
```bash
uvicorn main:app --reload --port 8001
```

### Estructura de Base de Datos

- **orders**: Tabla de órdenes (Order Service)
- **inventory_items**: Tabla de inventario (Inventory Service)  
- **payments**: Tabla de pagos (Payment Service)

## 📊 Monitoreo y Logs

Los logs de cada servicio incluyen:
- Eventos publicados y consumidos
- Operaciones de base de datos
- Retry attempts en Payment Service
- Notificaciones enviadas

```bash
# Ver logs en tiempo real
docker-compose logs -f order-service
docker-compose logs -f payment-service
```

## 🔒 Consideraciones de Producción

### Seguridad
- Implementar autenticación JWT
- Usar secrets para credenciales de DB
- Configurar HTTPS/TLS

### Escalabilidad
- Implementar circuit breakers
- Añadir rate limiting
- Configurar load balancing

### Observabilidad
- Integrar OpenTelemetry
- Configurar métricas con Prometheus
- Implementar distributed tracing

### Resilencia
- Implementar dead letter queues
- Configurar backup y recovery
- Añadir chaos engineering

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.