from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./resources.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(String)  # book, laptop, etc.
    status = Column(String)  # available, borrowed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Schemas
class ResourceBase(BaseModel):
    name: str
    description: str
    type: str

class ResourceCreate(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Database initialization
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Resource Service",
             description="Resource management service for the University Lending System",
             version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication middleware
async def verify_token(token: str):
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    try:
        response = requests.get(
            f"{auth_service_url}/validate-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Routes
@app.post("/resources/", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    db_resource = Resource(
        name=resource.name,
        description=resource.description,
        type=resource.type,
        status="available"
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/resources/", response_model=list[ResourceResponse])
async def list_resources(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    resources = db.query(Resource).offset(skip).limit(limit).all()
    return resources

@app.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@app.put("/resources/{resource_id}/status")
async def update_resource_status(
    resource_id: int,
    status: str,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if status not in ["available", "borrowed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    resource.status = status
    db.commit()
    return {"message": "Status updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
