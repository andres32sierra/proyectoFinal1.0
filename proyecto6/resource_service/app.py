from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime

app = FastAPI()

# Modelo de datos
class Resource(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    quantity: int
    status: str = "disponible"

# Configuración de la base de datos
DB_PATH = "resources.db"

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
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'disponible'
        )
    ''')
    
    # Verificar si hay recursos, si no hay, agregar algunos de ejemplo
    c.execute('SELECT COUNT(*) FROM resources')
    count = c.fetchone()[0]
    
    if count == 0:
        # Agregar recursos de ejemplo
        resources = [
            ('Laptop Dell XPS', 'Laptop para desarrollo', 1, 'disponible'),
            ('iPad Pro', 'Tablet para diseño', 1, 'disponible'),
            ('Proyector EPSON', 'Proyector para presentaciones', 1, 'disponible'),
            ('Cámara Sony', 'Cámara para fotografía', 1, 'disponible'),
            ('Monitor LG 4K', 'Monitor para diseño gráfico', 1, 'disponible')
        ]
        
        c.executemany(
            'INSERT INTO resources (name, description, quantity, status) VALUES (?, ?, ?, ?)',
            resources
        )
    
    conn.commit()
    conn.close()

init_db()

@app.post("/resources/", response_model=Resource)
def create_resource(resource: Resource):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO resources (name, description, quantity, status) VALUES (?, ?, ?, ?)",
            (resource.name, resource.description, resource.quantity, resource.status)
        )
        conn.commit()
        resource.id = c.lastrowid
        return resource
    finally:
        conn.close()

@app.get("/resources/")
def get_resources():
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM resources ORDER BY id")
        resources = c.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        result = [{
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "quantity": r[3],
            "status": r[4]
        } for r in resources]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return resources
    finally:
        conn.close()

@app.get("/resources/{resource_id}", response_model=Resource)
def get_resource(resource_id: int):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        row = c.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return Resource(
            id=row[0],
            name=row[1],
            description=row[2],
            quantity=row[3],
            status=row[4]
        )
    finally:
        conn.close()

@app.put("/resources/{resource_id}", response_model=Resource)
def update_resource(resource_id: int, resource: Resource):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(
            "UPDATE resources SET name = ?, description = ?, quantity = ?, status = ? WHERE id = ?",
            (resource.name, resource.description, resource.quantity, resource.status, resource_id)
        )
        conn.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        resource.id = resource_id
        return resource
    finally:
        conn.close()

@app.put("/resources/{resource_id}/status")
def update_resource_status(resource_id: int, status: dict):
    conn = get_db()
    try:
        c = conn.cursor()
        # Primero verificar si el recurso existe
        c.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        resource = c.fetchone()
        if not resource:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
            
        # Actualizar el estado
        c.execute(
            "UPDATE resources SET status = ? WHERE id = ?",
            (status.get("status"), resource_id)
        )
        conn.commit()
        
        # Verificar que la actualización fue exitosa
        c.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        updated_resource = c.fetchone()
        if updated_resource[4] != status.get("status"):
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar el estado del recurso"
            )
            
        return {"message": "Estado actualizado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
        conn.commit()
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        return {"message": "Recurso eliminado"}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
