# Universidad Central de Préstamos - Sistema de Gestión

Sistema de gestión de préstamos basado en una arquitectura de microservicios, implementado con FastAPI y Flask.

## Arquitectura del Sistema

### Backend (FastAPI)
El sistema utiliza FastAPI como framework principal para los microservicios, aprovechando sus características:
- Alto rendimiento y async/await
- Validación automática con Pydantic
- Documentación automática con Swagger/OpenAPI
- Seguridad con JWT y OAuth2
- Sistema de préstamos con control de cantidades múltiples

### Microservicios

1. **Auth Service** (Puerto 8000)
   - Gestión de autenticación y usuarios
   - JWT para manejo de sesiones
   - Encriptación de contraseñas con bcrypt

2. **Resource Service** (Puerto 8001)
   - Gestión de recursos prestables
   - CRUD completo de recursos
   - Control de cantidades y disponibilidad
   - Estado dinámico basado en unidades prestadas

3. **Student Service** (Puerto 8002)
   - Gestión de estudiantes
   - Perfiles y datos académicos

4. **Loan Service** (Puerto 8003)
   - Gestión de préstamos
   - Seguimiento de estados
   - Validaciones de disponibilidad
   - Soporte para préstamos de múltiples unidades
   - Verificación de cantidades disponibles

5. **Notification Service** (Puerto 8004)
   - Sistema de notificaciones
   - Integración con SendGrid

### Frontend (Flask)
- **Web Interface** (Puerto 5000)
  - Interfaz web con Flask y Jinja2
  - Integración con todos los microservicios

## Requisitos Técnicos

- Python 3.8+
- SQLite (incluido con Python)
- SendGrid API Key (para notificaciones)

## Instalación

1. **Crear un entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

Dependencias principales:
- FastAPI 0.104.1: Framework principal de APIs
- Uvicorn 0.24.0: Servidor ASGI
- SQLAlchemy 2.0.23: ORM
- Pydantic 2.5.1: Validación de datos
- Flask 3.0.0: Interfaz web

3. **Configurar variables de entorno:**
Crea un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu_clave_secreta
SENDGRID_API_KEY=tu_api_key_sendgrid
DATABASE_URL=sqlite:///./app.db
```

## Iniciar el Sistema

### Usando Scripts (Recomendado)
Utilizar los scripts proporcionados en la carpeta `scripts/`:
```bash
./scripts/start_auth.ps1
./scripts/start_resource.ps1
./scripts/start_loan.ps1
./scripts/start_notification.ps1
```

### Inicio Manual
Iniciar cada servicio en una terminal diferente:

```bash
# Auth Service (Puerto 8000)
cd auth_service && uvicorn main:app --reload --port 8000

# Resource Service (Puerto 8001)
cd resource_service && uvicorn main:app --reload --port 8001

# Loan Service (Puerto 8003)
cd loan_service && uvicorn main:app --reload --port 8003

# Notification Service (Puerto 8004)
cd notification_service && uvicorn main:app --reload --port 8004

# Web Interface (Puerto 5000)
cd web_interface && flask run
```

## Acceso al Sistema

### Interfaz Web
- URL: http://localhost:5000
- Credenciales por defecto:
  - Usuario: `admin`
  - Contraseña: `admin123`

### Documentación API (Swagger UI)
Cada microservicio incluye documentación automática generada por FastAPI:

- API Gateway: http://localhost:8080/docs
  - Dashboard: http://localhost:8080/dashboard
  - Métricas: http://localhost:8080/metrics

Servicios individuales:
- Auth Service: http://localhost:8000/docs
- Resource Service: http://localhost:8001/docs
- Loan Service: http://localhost:8003/docs
- Notification Service: http://localhost:8004/docs

### API Gateway Endpoints

El API Gateway expone los siguientes endpoints consolidados:

```http
# Autenticación
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET /api/v1/auth/verify

# Recursos
GET /api/v1/resources
POST /api/v1/resources
GET /api/v1/resources/{id}
PUT /api/v1/resources/{id}
DELETE /api/v1/resources/{id}

# Préstamos
GET /api/v1/loans
POST /api/v1/loans
GET /api/v1/loans/{id}
PUT /api/v1/loans/{id}/return

# Estudiantes
GET /api/v1/students
POST /api/v1/students
GET /api/v1/students/{id}
PUT /api/v1/students/{id}
DELETE /api/v1/students/{id}
```

Todos los endpoints del API Gateway:
- Requieren autenticación mediante token JWT
- Incluyen rate limiting
- Proporcionan caché automático
- Registran métricas de uso

### Documentación API (ReDoc)
Versión alternativa de la documentación:
- Agregar `/redoc` al final de cada URL de servicio
- Ejemplo: http://localhost:8000/redoc

## Funcionalidades del Sistema

### Gestión de Recursos
- Registro de recursos con cantidades múltiples
- Control de disponibilidad en tiempo real
- Estado dinámico basado en unidades prestadas
- Categorización por tipo de recurso

### Gestión de Préstamos
- Préstamos de múltiples unidades
- Validación automática de disponibilidad
- Fechas de vencimiento configurables
- Notificaciones automáticas
- Historial de préstamos por estudiante

### Gestión de Estudiantes
- Registro de estudiantes con datos académicos
- Historial de préstamos por estudiante
- Límites de préstamos configurables
- Notificaciones personalizadas

### Panel de Administración
- Dashboard con estadísticas en tiempo real
- Gestión de usuarios y permisos
- Reportes de préstamos y recursos
- Configuración del sistema

## Características Técnicas

### Seguridad
- Autenticación JWT
- Passwords hasheados con bcrypt
- CORS configurado
- Validación de datos con Pydantic

### Base de Datos
- SQLite por defecto
- Modelos SQLAlchemy
- Migraciones automáticas

### API REST
- Operaciones CRUD completas
- Validación de esquemas
- Manejo de errores HTTP
- Rate limiting
- Control de cantidades en préstamos
- Estado dinámico de recursos

### API Gateway
- Enrutamiento centralizado
- Load balancing
- Caché de respuestas
- Monitoreo de servicios
- Autenticación centralizada
- Logging de solicitudes

### Notificaciones
- Integración con SendGrid
- Plantillas de email
- Cola de notificaciones

## Diagrama de Arquitectura

```
+------------------+     +-------------------+     +------------------+
|   Web Interface  |     |    API Gateway    |     |  Auth Service    |
|    (Flask 5000) |<--->| (Traefik 8080)   |<--->|   (FastAPI 8000) |
+------------------+     +-------------------+     +------------------+
                                   |
        +---------------------------|---------------------------+
        |                          |                          |
+------------------+     +------------------+     +------------------+
| Resource Service |     |   Loan Service   |     | Student Service  |
| (FastAPI 8001)   |<--->| (FastAPI 8003)   |<--->| (FastAPI 8002)   |
+------------------+     +------------------+     +------------------+
        |                          |                          |
        |                  +------------------+                |
        |                  |    Notification  |                |
        +----------------->|     Service      |<---------------+
                           | (FastAPI 8004)   |
                           +------------------+
```

## Guía de Despliegue Detallada

### 1. Preparación del Entorno

```bash
# Clonar el repositorio
git clone <url-repositorio>
cd proyecto6

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración del API Gateway (Traefik)

```yaml
# traefik.yml
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":8080"
    http:
      middlewares:
        - rate-limit
        - auth
        - cors

metrics:
  prometheus: {}

providers:
  file:
    filename: routes.yml

# middlewares.yml
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
    auth:
      basicAuth:
        users:
          - "admin:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/"
    cors:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        accessControlAllowOriginList:
          - "http://localhost:5000"
        accessControlMaxAge: 100
        addVaryHeader: true

# routes.yml
http:
  routers:
    auth:
      rule: "PathPrefix(`/api/v1/auth`)"
      service: auth-service
      middlewares:
        - rate-limit
        - cors
    resource:
      rule: "PathPrefix(`/api/v1/resources`)"
      service: resource-service
      middlewares:
        - rate-limit
        - auth
        - cors
    loan:
      rule: "PathPrefix(`/api/v1/loans`)"
      service: loan-service
      middlewares:
        - rate-limit
        - auth
        - cors
    student:
      rule: "PathPrefix(`/api/v1/students`)"
      service: student-service
      middlewares:
        - rate-limit
        - auth
        - cors

  services:
    auth-service:
      loadBalancer:
        servers:
          - url: "http://localhost:8000"
    resource-service:
      loadBalancer:
        servers:
          - url: "http://localhost:8001"
    loan-service:
      loadBalancer:
        servers:
          - url: "http://localhost:8003"
    student-service:
      loadBalancer:
        servers:
          - url: "http://localhost:8002"
```

### 3. Iniciar Servicios en Orden

```bash
# 1. Iniciar API Gateway
docker-compose up -d traefik

# 2. Iniciar Auth Service
cd auth_service && uvicorn main:app --reload --port 8000

# 3. Iniciar otros servicios
./scripts/start_services.ps1
```

## Documentación de Endpoints Principales

### Auth Service (8000)
```http
# Login
POST /auth/login
Content-Type: application/json
{
    "username": "admin",
    "password": "admin123"
}

# Verificar Token
GET /auth/verify
Authorization: Bearer <token>
```

### Resource Service (8001)
```http
# Crear Recurso
POST /resources/
Content-Type: application/json
{
    "name": "Laptop",
    "quantity": 3,
    "type": "Computadora"
}

# Actualizar Cantidad
PATCH /resources/{id}/quantity
Content-Type: application/json
{
    "quantity": 5
}
```

### Loan Service (8003)
```http
# Crear Préstamo
POST /loans/
Content-Type: application/json
{
    "student_id": "A2023001",
    "resource_id": 1,
    "quantity": 2
}

# Devolver Préstamo
PUT /loans/{id}/return
```

## Guía de Troubleshooting

### Problemas Comunes y Soluciones

1. **Error de Conexión a Servicios**
   ```
   Error: Could not connect to service
   ```
   Solución:
   - Verificar que el servicio esté en ejecución
   - Comprobar el puerto correcto
   - Revisar logs del servicio

2. **Error en Préstamos Múltiples**
   ```
   Error: Resource quantity not available
   ```
   Solución:
   - Verificar cantidad disponible en recurso
   - Revisar estado de préstamos activos
   - Validar la actualización de cantidades

3. **Problemas de Autenticación**
   ```
   Error: Invalid token or expired
   ```
   Solución:
   - Renovar sesión
   - Limpiar caché del navegador
   - Verificar configuración de CORS

4. **Errores en Base de Datos**
   ```
   Error: Database is locked
   ```
   Solución:
   - Reiniciar el servicio afectado
   - Verificar permisos de archivos
   - Comprobar conexiones activas

5. **Problemas de Rendimiento**
   Solución:
   - Implementar caché en API Gateway
   - Optimizar consultas a base de datos
   - Monitorear uso de recursos

## Ejemplos de API

### Crear un Recurso
```http
POST /resources/
Content-Type: application/json

{
  "name": "Laptop Dell XPS",
  "description": "Laptop para desarrollo",
  "type": "Computadora",
  "quantity": 3,
  "status": "disponible"
}
```

### Crear un Préstamo
```http
POST /loans/
Content-Type: application/json

{
  "student_id": "A2023001",
  "resource_id": 1,
  "quantity": 2,
  "status": "prestado"
}
```

### Obtener Recursos Disponibles
```http
GET /resources/?status=disponible

Response:
[
  {
    "id": 1,
    "name": "Laptop Dell XPS",
    "quantity": 3,
    "loaned_quantity": 1,
    "status": "disponible"
  }
]
```
