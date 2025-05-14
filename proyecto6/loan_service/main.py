from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./loans.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer)
    student_id = Column(String)
    loan_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)
    status = Column(String)  # active, returned, overdue
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Schemas
class LoanBase(BaseModel):
    resource_id: int
    student_id: str
    due_date: datetime

class LoanCreate(LoanBase):
    pass

class LoanResponse(LoanBase):
    id: int
    loan_date: datetime
    return_date: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Database initialization
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Loan Service",
             description="Loan management service for the University Lending System",
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

# Helper functions
async def check_resource_availability(resource_id: int):
    resource_service_url = os.getenv("RESOURCE_SERVICE_URL", "http://localhost:8001")
    try:
        response = requests.get(f"{resource_service_url}/resources/{resource_id}")
        if response.status_code == 200:
            resource = response.json()
            return resource["status"] == "available"
        return False
    except:
        raise HTTPException(status_code=503, detail="Resource service unavailable")

async def check_student_exists(student_id: str):
    student_service_url = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")
    try:
        response = requests.get(f"{student_service_url}/students/{student_id}")
        return response.status_code == 200
    except:
        raise HTTPException(status_code=503, detail="Student service unavailable")

async def update_resource_status(resource_id: int, status: str, token: str):
    resource_service_url = os.getenv("RESOURCE_SERVICE_URL", "http://localhost:8001")
    try:
        response = requests.put(
            f"{resource_service_url}/resources/{resource_id}/status",
            params={"status": status},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.status_code == 200
    except:
        raise HTTPException(status_code=503, detail="Resource service unavailable")

async def send_notification(student_id: str, message: str):
    notification_service_url = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8004")
    try:
        requests.post(
            f"{notification_service_url}/notify",
            json={"student_id": student_id, "message": message}
        )
    except:
        # Log error but don't fail the request
        print(f"Failed to send notification to student {student_id}")

# Routes
@app.post("/loans/", response_model=LoanResponse)
async def create_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Validate resource availability
    if not await check_resource_availability(loan.resource_id):
        raise HTTPException(status_code=400, detail="Resource is not available")

    # Validate student exists
    if not await check_student_exists(loan.student_id):
        raise HTTPException(status_code=400, detail="Student not found")

    # Create loan
    db_loan = Loan(
        resource_id=loan.resource_id,
        student_id=loan.student_id,
        due_date=loan.due_date,
        status="active"
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)

    # Update resource status
    await update_resource_status(loan.resource_id, "borrowed", authorization)

    # Send notification
    await send_notification(
        loan.student_id,
        f"Resource {loan.resource_id} has been loaned to you. Due date: {loan.due_date}"
    )

    return db_loan

@app.get("/loans/", response_model=list[LoanResponse])
async def list_loans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    loans = db.query(Loan).offset(skip).limit(limit).all()
    return loans

@app.get("/loans/student/{student_id}", response_model=list[LoanResponse])
async def get_student_loans(
    student_id: str,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    loans = db.query(Loan).filter(Loan.student_id == student_id).all()
    return loans

@app.put("/loans/{loan_id}/return")
async def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.status == "returned":
        raise HTTPException(status_code=400, detail="Loan already returned")

    loan.return_date = datetime.utcnow()
    loan.status = "returned"
    db.commit()

    # Update resource status
    await update_resource_status(loan.resource_id, "available", authorization)

    # Send notification
    await send_notification(
        loan.student_id,
        f"Resource {loan.resource_id} has been returned successfully."
    )

    return {"message": "Loan returned successfully"}

@app.get("/loans/{loan_id}", response_model=LoanResponse)
async def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    authorization: str = Depends(verify_token)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
