from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os

app = FastAPI()

# Modelo de datos
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    student_id: str
    career: str
    semester: int

# Configuración de la base de datos
DB_PATH = "students.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla si no existe
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Crear la tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            career TEXT NOT NULL,
            semester INTEGER NOT NULL
        )
    ''')
    
    # Verificar si hay estudiantes, si no hay, agregar algunos de ejemplo
    c.execute('SELECT COUNT(*) FROM students')
    count = c.fetchone()[0]
    
    if count == 0:
        # Agregar estudiantes de ejemplo
        students = [
            ('Juan Pérez', 'juan.perez@universidad.edu', 'A2023001', 'Ingeniería', 1),
            ('María García', 'maria.garcia@universidad.edu', 'A2023002', 'Ingeniería', 2),
            ('Carlos López', 'carlos.lopez@universidad.edu', 'A2023003', 'Ingeniería', 3),
            ('Ana Martínez', 'ana.martinez@universidad.edu', 'A2023004', 'Ingeniería', 4),
            ('Luis Rodríguez', 'luis.rodriguez@universidad.edu', 'A2023005', 'Ingeniería', 5)
        ]
        
        c.executemany(
            'INSERT INTO students (name, email, student_id, career, semester) VALUES (?, ?, ?, ?, ?)',
            students
        )
        
    conn.commit()
    conn.close()

init_db()

@app.post("/students/", response_model=Student)
def create_student(student: Student):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO students (name, email, student_id, career, semester) VALUES (?, ?, ?, ?, ?)",
            (student.name, student.email, student.student_id, student.career, student.semester)
        )
        conn.commit()
        student.id = c.lastrowid
        return student
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El ID de estudiante ya existe")
    finally:
        conn.close()

@app.get("/students/")
def get_students():
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT id, name, email, student_id, career, semester FROM students ORDER BY id")
        students = c.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        result = [{
            "id": s[0],
            "name": s[1],
            "email": s[2],
            "student_id": s[3],
            "career": s[4],
            "semester": s[5]
        } for s in students]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = c.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return Student(
            id=row[0],
            name=row[1],
            email=row[2],
            student_id=row[3],
            career=row[4],
            semester=row[5]
        )
    finally:
        conn.close()

@app.get("/students/by-student-id/{student_code}", response_model=Student)
def get_student_by_code(student_code: str):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id = ?", (student_code,))
        row = c.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return Student(
            id=row[0],
            name=row[1],
            email=row[2],
            student_id=row[3],
            career=row[4],
            semester=row[5]
        )
    finally:
        conn.close()

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: Student):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(
            """UPDATE students 
               SET name = ?, email = ?, student_id = ?, career = ?, semester = ? 
               WHERE id = ?""",
            (student.name, student.email, student.student_id, student.career, 
             student.semester, student_id)
        )
        conn.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        student.id = student_id
        return student
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El ID de estudiante ya existe")
    finally:
        conn.close()

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return {"message": "Estudiante eliminado"}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
