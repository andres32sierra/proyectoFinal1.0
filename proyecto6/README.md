# Universidad Central de Préstamos - Sistema de Gestión

Sistema de gestión de préstamos basado en microservicios para la Universidad.

## Microservicios

- Auth Service (Puerto 8000): Gestión de autenticación y usuarios
- Resource Service (Puerto 8001): Gestión de recursos prestables
- Student Service (Puerto 8002): Gestión de estudiantes
- Loan Service (Puerto 8003): Gestión de préstamos
- Notification Service (Puerto 8004): Sistema de notificaciones
- Web Interface (Puerto 5000): Interfaz web Flask

## Instalación

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
SECRET_KEY=tu_clave_secreta
SENDGRID_API_KEY=tu_api_key_sendgrid
```

## Iniciar el Sistema

1. Iniciar todos los microservicios (ejecutar cada comando en una terminal diferente):

```bash
# Auth Service
cd auth_service
python app.py

# Resource Service
cd resource_service
python app.py

# Student Service
cd student_service
python app.py

# Loan Service
cd loan_service
python app.py

# Notification Service
cd notification_service
python app.py

# Web Interface
cd web_interface
python app.py
```

2. Acceder a la interfaz web:
Abrir en el navegador: http://localhost:5000

## Credenciales por defecto

Usuario: admin
Contraseña: admin123

4. Iniciar los servicios:
Ejecutar cada servicio en una terminal diferente usando los scripts en la carpeta `scripts/`

## Documentación API

- Auth Service: http://localhost:8000/docs
- Resource Service: http://localhost:8001/docs
- Student Service: http://localhost:8002/docs
- Loan Service: http://localhost:8003/docs
- Notification Service: http://localhost:8004/docs

## Interfaz Web
Acceder a http://localhost:5000
