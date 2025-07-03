from sqlalchemy.orm import Session
from models import Medicine
from schemas import MedicineCreate, MedicineUpdate

def get_medicines(db: Session):
    return db.query(Medicine).all()

def get_medicine(db: Session, medicine_id: int):
    return db.query(Medicine).filter(Medicine.id == medicine_id).first()

def create_medicine(db: Session, medicine: MedicineCreate):
    db_medicine = Medicine(name=medicine.name, price=medicine.price)
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: MedicineUpdate):
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        if medicine.name is not None:
            db_medicine.name = medicine.name
        if medicine.price is not None:
            db_medicine.price = medicine.price
        db.commit()
        db.refresh(db_medicine)
    return db_medicine


def delete_medicine(db: Session, medicine_id: int):
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        db.delete(db_medicine)
        db.commit()
    return db_medicine
