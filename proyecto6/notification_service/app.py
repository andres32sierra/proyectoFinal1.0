from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
STUDENT_SERVICE_URL = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")
FROM_EMAIL = os.getenv("FROM_EMAIL", "universidad@example.com")

# Modelo de datos
class Notification(BaseModel):
    student_id: str
    message: str

def get_student_email(student_id: str):
    try:
        response = requests.get(f"{STUDENT_SERVICE_URL}/students/by-student-id/{student_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        student = response.json()
        return student["email"]
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Servicio de estudiantes no disponible")

@app.post("/notify")
async def send_notification(notification: Notification):
    try:
        # Obtener el email del estudiante
        student_email = get_student_email(notification.student_id)
        
        # Crear el mensaje
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=student_email,
            subject='Notificación del Sistema de Préstamos',
            html_content=notification.message
        )
        
        # Enviar el email si hay API key configurada
        if SENDGRID_API_KEY:
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                response = sg.send(message)
                return {"status": "success", "message": "Notificación enviada"}
            except Exception as e:
                print(f"Error al enviar email: {str(e)}")
                return {"status": "error", "message": "Error al enviar la notificación por email"}
        else:
            # Si no hay API key, solo simulamos el envío
            print(f"Simulando envío de email a {student_email}: {notification.message}")
            return {"status": "success", "message": "Notificación simulada"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
