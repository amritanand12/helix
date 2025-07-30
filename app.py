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

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=9758, workers=8)
