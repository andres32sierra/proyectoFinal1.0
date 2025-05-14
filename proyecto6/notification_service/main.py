from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests

load_dotenv()

# Constants
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "universidad@example.com"  # Replace with your verified sender

# FastAPI app
app = FastAPI(title="Notification Service",
             description="Notification service for the University Lending System",
             version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class NotificationRequest(BaseModel):
    student_id: str
    message: str

async def get_student_email(student_id: str):
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")
    try:
        response = requests.get(f"{student_service_url}/students/{student_id}")
        if response.status_code == 200:
            student = response.json()
            return student["email"]
        return None
    except:
        return None

async def send_email(to_email: str, message: str):
    if not SENDGRID_API_KEY:
        print(f"Would send email to {to_email}: {message}")
        return True
        
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        mail = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject='Universidad Central de Préstamos - Notificación',
            html_content=f'<p>{message}</p>'
        )
        response = sg.send(mail)
        return response.status_code == 202
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

@app.post("/notify")
async def send_notification(notification: NotificationRequest):
    # Get student email
    student_email = await get_student_email(notification.student_id)
    if not student_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Send email notification
    success = await send_email(student_email, notification.message)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )
    
    return {"message": "Notification sent successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
