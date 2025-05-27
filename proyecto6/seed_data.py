import sqlite3
import os
from datetime import datetime, timedelta

def init_resources():
    conn = sqlite3.connect('resource_service/resources.db')
    c = conn.cursor()
    
    # Limpiar tabla si existe
    c.execute('DROP TABLE IF EXISTS resources')
    
    # Crear tabla
    c.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'disponible'
        )
    ''')
    
    # Datos de ejemplo
    resources = [
        ('Laptop Dell XPS', 'Laptop para desarrollo de software', 'Computadora', 5, 'disponible'),
        ('Proyector Epson', 'Proyector para presentaciones', 'Equipo Audiovisual', 3, 'disponible'),
        ('iPad Pro', 'Tablet para diseño gráfico', 'Tablet', 4, 'disponible'),
        ('Monitor LG 27"', 'Monitor para estación de trabajo', 'Monitor', 6, 'disponible'),
        ('Cámara Sony', 'Cámara para fotografía profesional', 'Equipo Fotográfico', 2, 'disponible')
    ]
    
    c.executemany('INSERT INTO resources (name, description, type, quantity, status) VALUES (?, ?, ?, ?, ?)', resources)
    conn.commit()
    conn.close()

def init_students():
    conn = sqlite3.connect('student_service/students.db')
    c = conn.cursor()
    
    # Limpiar tabla si existe
    c.execute('DROP TABLE IF EXISTS students')
    
    # Crear tabla
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
    
    # Datos de ejemplo
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
    
    c.executemany('INSERT INTO students (name, email, student_id, career, semester, phone) VALUES (?, ?, ?, ?, ?, ?)', students)
    conn.commit()
    conn.close()

def init_loans():
    conn = sqlite3.connect('loan_service/loans.db')
    c = conn.cursor()
    
    # Limpiar tabla si existe
    c.execute('DROP TABLE IF EXISTS loans')
    
    # Crear tabla
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'prestado'
        )
    ''')
    
    # Datos de ejemplo - algunos préstamos activos y otros devueltos
    current_time = datetime.now()
    loans = [
        # Préstamos activos
        (1, 1, current_time.isoformat(), (current_time + timedelta(days=7)).isoformat(), None, 'prestado'),
        (2, 2, current_time.isoformat(), (current_time + timedelta(days=7)).isoformat(), None, 'prestado'),
        # Préstamos devueltos
        (3, 3, (current_time - timedelta(days=14)).isoformat(), 
         (current_time - timedelta(days=7)).isoformat(),
         (current_time - timedelta(days=6)).isoformat(), 'devuelto'),
        (4, 4, (current_time - timedelta(days=21)).isoformat(),
         (current_time - timedelta(days=14)).isoformat(),
         (current_time - timedelta(days=15)).isoformat(), 'devuelto')
    ]
    
    c.executemany('''
        INSERT INTO loans (resource_id, student_id, loan_date, due_date, return_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', loans)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Inicializando bases de datos con datos de ejemplo...")
    
    # Crear directorios si no existen
    os.makedirs('resource_service', exist_ok=True)
    os.makedirs('student_service', exist_ok=True)
    os.makedirs('loan_service', exist_ok=True)
    
    init_resources()
    print("✓ Recursos inicializados")
    
    init_students()
    print("✓ Estudiantes inicializados")
    
    init_loans()
    print("✓ Sistema de préstamos inicializado")
    
    print("\n¡Datos de ejemplo creados exitosamente!")
