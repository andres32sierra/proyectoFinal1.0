from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="API Gateway", description="Gateway para los microservicios del sistema de préstamos")

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API Gateway", "services": list(SERVICES.keys())}

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de los servicios
SERVICES = {
    "auth": "http://localhost:8000",
    "resource": "http://localhost:8001",
    "student": "http://localhost:8002",
    "loan": "http://localhost:8003",
    "notification": "http://localhost:8004"
}

async def proxy_request(service: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    client = httpx.AsyncClient()
    
    # Construir la URL del servicio destino
    url = f"{SERVICES[service]}{request.url.path.replace(f'/api/{service}', '')}"
    
    # Obtener el cuerpo de la petición
    body = await request.body()
    
    try:
        # Realizar la petición al servicio correspondiente
        response = await client.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers.items() if key.lower() not in ['host', 'content-length']},
            content=body,
            params=request.query_params,
        )
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.aclose()

# Rutas para cada servicio
@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    return await proxy_request(service, request)

# Ruta de estado de salud
@app.get("/health")
async def health_check():
    status = {}
    async with httpx.AsyncClient() as client:
        for service, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=2.0)
                status[service] = "up" if response.status_code == 200 else "down"
            except:
                status[service] = "down"
    return {"status": "up", "services": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
