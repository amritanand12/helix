from sqlalchemy.orm import Session
from models import Medicine
from schemas import MedicineCreate, MedicineUpdate
from sqlalchemy import func
from fastapi import HTTPException
from typing import Optional

def get_medicines(db: Session, search: Optional[str] = None, page: int = 1, limit: int = 10):
    query = db.query(Medicine)

    # If there's a search term, filter medicines based on it (case-insensitive search on name)
    if search:
        query = query.filter(
            func.lower(Medicine.name).like(f"%{search.lower()}%")
        )

    # Apply pagination
    skip = (page - 1) * limit
    medicines = query.offset(skip).limit(limit).all()

    return medicines

def get_medicine(db: Session, medicine_id: int):
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()

def create_medicine(db: Session, medicine: MedicineCreate):
    # Check for duplicates (case-insensitive) by name
    existing = db.query(Medicine).filter(
        (func.lower(Medicine.name) == func.lower(medicine.name))
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="A medicine with this name already exists.")

    # Create new medicine entry
    db_medicine = Medicine(name=medicine.name, price=medicine.price)

    try:
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
    except Exception as e:
        print(e)
        db.rollback()  # Rollback on error
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while saving the medicine. Please try again later."
        )
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: MedicineUpdate):
    # Fetch the medicine record from the database
    db_medicine = get_medicine(db, medicine_id)
    
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

    try:
        # Check for duplicates (case-insensitive) by name
        if medicine.name:
            existing = db.query(Medicine).filter(
                func.lower(Medicine.name) == func.lower(medicine.name)
            ).first()
            if existing and existing.id != medicine_id:
                raise HTTPException(status_code=400, detail="A medicine with this name already exists.")

        # Update the fields if provided
        if medicine.name is not None:
            db_medicine.name = medicine.name
        if medicine.price is not None:
            db_medicine.price = medicine.price

        # Commit the changes to the database
        db.commit()
        db.refresh(db_medicine)
        
    except Exception as e:
        db.rollback()  # Rollback on error
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the medicine. Please try again later."
        )
    
    return db_medicine


def delete_medicine(db: Session, medicine_id: int):
    # Fetch the medicine record from the database
    db_medicine = get_medicine(db, medicine_id)
    
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

    try:
        # Delete the medicine record
        db.delete(db_medicine)
        db.commit()
    except Exception as e:
        db.rollback()  # Rollback in case of any error during deletion
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the medicine. Please try again later."
        )

    return db_medicine
