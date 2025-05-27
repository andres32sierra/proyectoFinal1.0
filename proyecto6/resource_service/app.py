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
    type: str
    quantity: int
    loaned_quantity: int = 0
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
            type TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            loaned_quantity INTEGER DEFAULT 0,
            status TEXT DEFAULT 'disponible'
        )
    ''')
    
    # Verificar si hay recursos, si no hay, agregar algunos de ejemplo
    c.execute('SELECT COUNT(*) FROM resources')
    count = c.fetchone()[0]
    
    if count == 0:
        # Agregar recursos de ejemplo
        resources = [
            ('Laptop Dell XPS', 'Laptop para desarrollo de software', 'Computadora', 1, 0, 'disponible'),
            ('iPad Pro', 'Tablet para diseño gráfico', 'Tablet', 1, 0, 'disponible'),
            ('Proyector EPSON', 'Proyector para presentaciones', 'Equipo Audiovisual', 1, 0, 'disponible'),
            ('Cámara Sony', 'Cámara para fotografía profesional', 'Equipo Fotográfico', 1, 0, 'disponible'),
            ('Monitor LG 4K', 'Monitor para diseño gráfico', 'Monitor', 1, 0, 'disponible')
        ]
        
        c.executemany(
            'INSERT INTO resources (name, description, type, quantity, loaned_quantity, status) VALUES (?, ?, ?, ?, ?, ?)',
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
            "INSERT INTO resources (name, description, type, quantity, loaned_quantity, status) VALUES (?, ?, ?, ?, ?, ?)",
            (resource.name, resource.description, resource.type, resource.quantity, 0, resource.status)
        )
        conn.commit()
        resource.id = c.lastrowid
        resource.loaned_quantity = 0
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
            "type": r[3],
            "quantity": r[4],
            "loaned_quantity": r[5],
            "status": r[6]
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
            type=row[3],
            quantity=row[4],
            loaned_quantity=row[5],
            status=row[6]
        )
    finally:
        conn.close()

@app.put("/resources/{resource_id}", response_model=Resource)
def update_resource(resource_id: int, resource: Resource):
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute(
            "UPDATE resources SET name = ?, description = ?, type = ?, quantity = ?, status = ? WHERE id = ?",
            (resource.name, resource.description, resource.type, resource.quantity, resource.status, resource_id)
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
            
        # Validar que el estado sea válido
        new_status = status.get("status")
        if not new_status or new_status not in ["disponible", "prestado"]:
            raise HTTPException(status_code=400, detail="Estado inválido")
            
        # Obtener la cantidad total y prestada
        quantity = resource[4]
        loaned_quantity = resource[5]
        current_status = resource[6]
        
        if new_status == "prestado":
            # Verificar si hay unidades disponibles para prestar
            if loaned_quantity >= quantity:
                raise HTTPException(
                    status_code=400,
                    detail="No hay unidades disponibles para prestar"
                )
            # Incrementar la cantidad prestada
            loaned_quantity += 1
        else:  # status == "disponible"
            # Decrementar la cantidad prestada
            if loaned_quantity > 0:
                loaned_quantity -= 1
                
        # Determinar el estado basado en la cantidad prestada
        new_status = "prestado" if loaned_quantity > 0 else "disponible"
            
        # Actualizar el estado y la cantidad prestada
        c.execute(
            "UPDATE resources SET status = ?, loaned_quantity = ? WHERE id = ?",
            (new_status, loaned_quantity, resource_id)
        )
        conn.commit()
        
        # Verificar que la actualización fue exitosa
        c.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
        updated_resource = c.fetchone()
        
        # La actualización es exitosa si:
        # 1. La cantidad prestada se actualizó correctamente
        # 2. El estado refleja correctamente si hay o no unidades disponibles
        updated_loaned = updated_resource[5]
        updated_status = updated_resource[6]
        
        if updated_loaned != loaned_quantity:
            conn.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar la cantidad prestada"
            )
            
        expected_status = "prestado" if updated_loaned > 0 else "disponible"
        if updated_status != expected_status:
            conn.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar el estado del recurso"
            )
            
        return {
            "message": "Estado actualizado exitosamente",
            "status": new_status,
            "loaned_quantity": loaned_quantity,
            "available_quantity": quantity - loaned_quantity
        }
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
