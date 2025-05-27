import pytest
from fastapi.testclient import TestClient
from api_gateway.main import app
import responses

client = TestClient(app)

@pytest.fixture(scope="module")
def test_client():
    """Fixture para el cliente de pruebas"""
    return client

def test_servidor_responde(test_client):
    """Prueba que el servidor responda correctamente"""
    response = test_client.get('/')
    assert response.status_code == 200

def test_formato_json(test_client):
    """Prueba que el servidor devuelva formato JSON"""
    response = test_client.get('/')
    assert response.headers['content-type'].startswith('application/json')

def test_contenido_respuesta(test_client):
    """Prueba el contenido específico de la respuesta"""
    response = test_client.get('/')
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert "services" in data
    assert isinstance(data["services"], list)

def test_servicio_invalido(test_client):
    """Prueba el manejo de servicios inválidos"""
    response = test_client.get('/api/servicio_invalido/endpoint')
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Servicio no encontrado" in data["detail"]

@responses.activate
def test_error_servidor():
    """Prueba el comportamiento cuando un servicio está caído"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
