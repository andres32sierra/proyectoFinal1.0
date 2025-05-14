from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración de servicios
RESOURCE_SERVICE_URL = os.getenv("RESOURCE_SERVICE_URL", "http://localhost:8001")
STUDENT_SERVICE_URL = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")

# Modelo de datos
class Loan(BaseModel):
    id: Optional[int] = None
    student_id: str
    resource_id: int
    loan_date: Optional[str] = None
    due_date: Optional[str] = None
    return_date: Optional[str] = None
    status: str = "prestado"  # prestado, devuelto, vencido

# Configuración de la base de datos
DB_PATH = "loans.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla si no existe
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            resource_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT DEFAULT 'prestado'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def verify_student(student_id: str):
    try:
        response = requests.get(f"{STUDENT_SERVICE_URL}/students/by-student-id/{student_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return response.json()
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Servicio de estudiantes no disponible")

def verify_resource(resource_id: int):
    try:
        response = requests.get(f"{RESOURCE_SERVICE_URL}/resources/{resource_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        resource = response.json()
        if resource["status"] != "disponible":
            raise HTTPException(status_code=400, detail="Recurso no disponible")
        return resource
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Servicio de recursos no disponible")

def update_resource_status(resource_id: int, status: str):
    try:
        # Primero obtenemos el recurso actual
        response = requests.get(f"{RESOURCE_SERVICE_URL}/resources/{resource_id}")
        if response.status_code == 200:
            resource = response.json()
            resource["status"] = status
            # Actualizamos el estado
            update_response = requests.put(
                f"{RESOURCE_SERVICE_URL}/resources/{resource_id}",
                json=resource
            )
            if update_response.status_code != 200:
                raise HTTPException(status_code=500, detail="Error al actualizar el estado del recurso")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Servicio de recursos no disponible")

def send_notification(student_id: str, message: str):
    try:
        notification_data = {
            "student_id": student_id,
            "message": message
        }
        requests.post(f"{NOTIFICATION_SERVICE_URL}/notify", json=notification_data)
    except requests.RequestException:
        # No interrumpimos el proceso si falla la notificación
        pass

@app.post("/loans/", response_model=Loan)
def create_loan(loan: Loan):
    # Verificar estudiante y recurso
    student = verify_student(loan.student_id)
    resource = verify_resource(loan.resource_id)
    
    # Crear el préstamo
    conn = get_db()
    try:
        c = conn.cursor()
        now = datetime.now()
        loan.loan_date = now.isoformat()
        # Establecer fecha de vencimiento a 7 días después
        due_date = (now + timedelta(days=7)).isoformat()
        
        c.execute(
            "INSERT INTO loans (student_id, resource_id, loan_date, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (loan.student_id, loan.resource_id, loan.loan_date, due_date, loan.status)
        )
        conn.commit()
        loan.id = c.lastrowid
        
        # Actualizar estado del recurso
        update_resource_status(loan.resource_id, "prestado")
        
        # Enviar notificación
        send_notification(
            loan.student_id,
            f"Se ha registrado un préstamo del recurso {resource['name']}. "
            f"Por favor, devuélvelo antes del {due_date.split('T')[0]}."
        )
        
        return loan
    finally:
        conn.close()

@app.get("/loans/")
def get_loans():
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM loans ORDER BY id")
        loans = c.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        result = [{
            "id": l[0],
            "student_id": str(l[1]),  # Convertir a string
            "resource_id": str(l[2]),  # Convertir a string
            "loan_date": l[3],
            "due_date": l[4],
            "return_date": l[5],
            "status": l[6]
        } for l in loans]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/loans/{loan_id}", response_model=Loan)
def get_loan(loan_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
    row = c.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return Loan(
        id=row[0],
        student_id=row[1],
        resource_id=row[2],
        loan_date=row[3],
        due_date=row[4],
        return_date=row[5],
        status=row[6]
    )

@app.put("/loans/{loan_id}", response_model=Loan)
def update_loan(loan_id: int, loan: Loan):
    conn = get_db()
    try:
        # Primero verificar si el préstamo existe
        c = conn.cursor()
        c.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        existing_loan = c.fetchone()
        if not existing_loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        
        # Actualizar el préstamo
        c.execute(
            "UPDATE loans SET status = ?, return_date = ? WHERE id = ?",
            (loan.status, loan.return_date, loan_id)
        )
        conn.commit()
        
        # Obtener el préstamo actualizado
        c.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        updated_loan = c.fetchone()
        return Loan(
            id=updated_loan[0],
            student_id=updated_loan[1],
            resource_id=updated_loan[2],
            loan_date=updated_loan[3],
            due_date=updated_loan[4],
            return_date=updated_loan[5],
            status=updated_loan[6]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/loans/student/{student_id}", response_model=List[Loan])
def get_student_loans(student_id: str):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM loans WHERE student_id = ?", (student_id,))
        loans = []
        for row in c.fetchall():
            loans.append(
                Loan(
                    id=row[0],
                    student_id=row[1],
                    resource_id=row[2],
                    loan_date=row[3],
                    due_date=row[4],
                    return_date=row[5],
                    status=row[6]
                )
            )
        return loans
    finally:
        conn.close()

@app.put("/loans/{loan_id}/return", response_model=Loan)
def return_loan(loan_id: int):
    conn = get_db()
    try:
        c = conn.cursor()
        
        # Verificar que el préstamo existe y está activo
        c.execute("SELECT * FROM loans WHERE id = ? AND status = 'prestado'", (loan_id,))
        row = c.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado o ya devuelto")
        
        # Actualizar el préstamo
        return_date = datetime.now().isoformat()
        c.execute(
            "UPDATE loans SET status = 'devuelto', return_date = ? WHERE id = ?",
            (return_date, loan_id)
        )
        conn.commit()
        
        # Actualizar estado del recurso
        resource_id = row[2]
        update_resource_status(resource_id, "disponible")
        
        # Enviar notificación
        send_notification(
            row[1],  # student_id
            f"Se ha registrado la devolución del recurso correctamente."
        )
        
        return Loan(
            id=loan_id,
            student_id=row[1],
            resource_id=resource_id,
            loan_date=row[3],
            return_date=return_date,
            status="devuelto"
        )
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
