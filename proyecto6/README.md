# Universidad Central de Préstamos - Sistema de Gestión

Sistema de gestión de préstamos basado en una arquitectura de microservicios, implementado con FastAPI y Flask.

## Arquitectura del Sistema

### Backend (FastAPI)
El sistema utiliza FastAPI como framework principal para los microservicios, aprovechando sus características:
- Alto rendimiento y async/await
- Validación automática con Pydantic
- Documentación automática con Swagger/OpenAPI
- Seguridad con JWT y OAuth2

### Microservicios

1. **Auth Service** (Puerto 8000)
   - Gestión de autenticación y usuarios
   - JWT para manejo de sesiones
   - Encriptación de contraseñas con bcrypt

2. **Resource Service** (Puerto 8001)
   - Gestión de recursos prestables
   - CRUD completo de recursos
   - Estado de disponibilidad

3. **Student Service** (Puerto 8002)
   - Gestión de estudiantes
   - Perfiles y datos académicos

4. **Loan Service** (Puerto 8003)
   - Gestión de préstamos
   - Seguimiento de estados
   - Validaciones de disponibilidad

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

- Auth Service: http://localhost:8000/docs
- Resource Service: http://localhost:8001/docs
- Loan Service: http://localhost:8003/docs
- Notification Service: http://localhost:8004/docs

### Documentación API (ReDoc)
Versión alternativa de la documentación:
- Agregar `/redoc` al final de cada URL de servicio
- Ejemplo: http://localhost:8000/redoc

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

### Notificaciones
- Integración con SendGrid
- Plantillas de email
- Cola de notificaciones
