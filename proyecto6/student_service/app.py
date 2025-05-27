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
    phone: Optional[str] = None

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
            semester INTEGER NOT NULL,
            phone TEXT
        )
    ''')
    
    # Verificar si hay estudiantes, si no hay, agregar algunos de ejemplo
    c.execute('SELECT COUNT(*) FROM students')
    count = c.fetchone()[0]
    
    if count == 0:
        # Agregar estudiantes de ejemplo
        students = [
            ('Ana García', 'ana.garcia@universidad.edu', 'A2023001', 'Ingeniería de Software', 4, '555-1234'),
            ('Carlos Rodríguez', 'carlos.rodriguez@universidad.edu', 'A2023002', 'Diseño Gráfico', 3, '555-5678'),
            ('María López', 'maria.lopez@universidad.edu', 'A2023003', 'Ciencias de la Computación', 5, '555-9012'),
            ('Juan Martínez', 'juan.martinez@universidad.edu', 'A2023004', 'Sistemas de Información', 4, '555-3456'),
            ('Laura Torres', 'laura.torres@universidad.edu', 'A2023005', 'Ingeniería de Software', 3, '555-7890'),
            ('Andrés Diego', 'aandresdiego@gmail.com', '123', 'ing sistemas', 6, '555-2468'),
            ('Jennifer Velandia', 'jenifer.velandia@uniminuto.edu.co', '783129', 'ing sistemas', 8, '555-1357'),
            ('Andrés Diego', 'aandresdiego@gmail.com', 'A835173', 'ing sistemas', 7, '555-9753')
        ]
        
        c.executemany(
            'INSERT INTO students (name, email, student_id, career, semester, phone) VALUES (?, ?, ?, ?, ?, ?)',
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
            "INSERT INTO students (name, email, student_id, career, semester, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (student.name, student.email, student.student_id, student.career, student.semester, student.phone)
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
        c.execute("SELECT id, name, email, student_id, career, semester, phone FROM students ORDER BY id")
        students = c.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        result = [{
            "id": s[0],
            "name": s[1],
            "email": s[2],
            "student_id": s[3],
            "career": s[4],
            "semester": s[5],
            "phone": s[6]
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
            semester=row[5],
            phone=row[6]
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
            semester=row[5],
            phone=row[6]
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
               SET name = ?, email = ?, student_id = ?, career = ?, semester = ?, phone = ? 
               WHERE id = ?""",
            (student.name, student.email, student.student_id, student.career, 
             student.semester, student.phone, student_id)
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
