from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models, schemas, crud
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from database import engine, SessionLocal
from crud import get_medicines

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],
)

@app.post("/medicines", response_model=schemas.MedicineOut)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    return crud.create_medicine(db, medicine)

@app.get("/medicines", response_model=List[schemas.MedicineOut])
def read_medicines(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, min_length=3, max_length=100),  # Optional search query
    page: int = Query(1, ge=1),  # Pagination: default page is 1, must be >= 1
    limit: int = Query(10, le=100),  # Pagination: limit to max 100 results per page
):
    """
    Fetch medicines with optional search and pagination.
    - `search`: Search query to filter medicines.
    - `page`: Page number for pagination.
    - `limit`: Number of items per page.
    """
    return get_medicines(db, search=search, page=page, limit=limit)

@app.get("/medicines/{medicine_id}", response_model=schemas.MedicineOut)
def read_medicine(medicine_id: int, db: Session = Depends(get_db)):
    db_medicine = crud.get_medicine(db, medicine_id)
    if db_medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return db_medicine

@app.patch("/medicines/{medicine_id}", response_model=schemas.MedicineOut)
def patch_medicine(medicine_id: int, medicine: schemas.MedicineUpdate, db: Session = Depends(get_db)):
    db_medicine = crud.update_medicine(db, medicine_id, medicine)
    if db_medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return db_medicine

@app.delete("/medicines/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    db_medicine = crud.delete_medicine(db, medicine_id)
    if db_medicine is None:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return {"message": "Medicine deleted successfully"}

@app.get("/bills", response_model=List[schemas.BillOut])
def read_bills(
    db: Session = Depends(get_db),
    customer_name: Optional[str] = Query(None, min_length=3, max_length=100),  # Optional customer name filter
    page: int = Query(1, ge=1),  # Pagination: default page is 1, must be >= 1
    limit: int = Query(10, le=100),  # Pagination: limit to max 100 results per page
):
    """
    Fetch bills with optional customer name filter and pagination.
    - `customer_name`: Filter bills by customer name.
    - `page`: Page number for pagination.
    - `limit`: Number of items per page.
    """
    return crud.get_bills(db, customer_name=customer_name, page=page, limit=limit)

# @app.post("/bills", response_model=schemas.BillOut)
# def create_bill(bill: schemas.BillCreate,customer:schemas.CustomerCreate, bill_items: List[schemas.BillItemCreate],db: Session = Depends(get_db)):
#     return crud.create_bill(db, bill,customer,bill_items)

# You should define a Pydantic model that nests bill, customer, and bill_items
@app.post("/bills", response_model=schemas.BillOut)
def create_bill(bill_data: schemas.BillCreateNested, db: Session = Depends(get_db)):
    return crud.create_bill(db, bill_data)

@app.get("/bills/{bill_id}", response_model=schemas.BillOut)
def read_bill(bill_id: int, db: Session = Depends(get_db)):
    db_bill = crud.get_bill(db, bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill

@app.delete("/bills/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    db_bill = crud.delete_bill(db, bill_id)
    if db_bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=9758, reload=True)
