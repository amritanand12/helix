from sqlalchemy.orm import Session
from models import Medicine, Customer, Bill, BillItem
from schemas import MedicineCreate, MedicineUpdate, CustomerCreate, CustomerUpdate, BillCreate, BillUpdate, BillItemCreate, BillItemUpdate, BillCreateNested
from sqlalchemy import func
from fastapi import HTTPException
from typing import Optional, List

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
    except Exception:
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail="An unexpected error occurred while saving the medicine.")
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: MedicineUpdate):
    # Fetch the medicine record from the database
    db_medicine = get_medicine(db, medicine_id)
    
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

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

    try:
        db.commit()
        db.refresh(db_medicine)
    except Exception:
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the medicine.")
    
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
    except Exception:
        db.rollback()  # Rollback in case of any error during deletion
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the medicine.")

    return db_medicine

# Similar CRUD functions can be created for Customer, Bill, and BillItem following the same patterns.
def get_customers(db: Session, search: Optional[str] = None, page: int = 1, limit: int = 10):
    query = db.query(Customer)

    # If there's a search term, filter customers based on it (case-insensitive search on name, phone, email)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            func.lower(Customer.name).like(search_term) |
            func.lower(Customer.phone).like(search_term) |
            func.lower(Customer.email).like(search_term)
        )

    # Apply pagination
    skip = (page - 1) * limit
    customers = query.offset(skip).limit(limit).all()

    return customers

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()    

def create_customer(db: Session, customer: CustomerCreate):
    # Check for duplicates (case-insensitive) by phone or email
    existing = db.query(Customer).filter(
        (func.lower(Customer.phone) == func.lower(customer.phone)) |
        (func.lower(Customer.email) == func.lower(customer.email))
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="A customer with this phone or email already exists.")

    # Create new customer entry
    db_customer = Customer(
        name=customer.name, 
        phone=customer.phone, 
        email=customer.email,
        address=customer.address
    )

    try:
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
    except Exception:
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail="An unexpected error occurred while saving the customer.")
    return db_customer

def update_customer(db: Session, customer_id: int, customer: CustomerUpdate):
    # Fetch the customer record from the database
    db_customer = get_customer(db, customer_id)
    
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Check for duplicates (case-insensitive) by phone or email
    if customer.phone or customer.email:
        existing = db.query(Customer).filter(
            (func.lower(Customer.phone) == func.lower(customer.phone)) |
            (func.lower(Customer.email) == func.lower(customer.email))
        ).first()
        if existing and existing.id != customer_id:
            raise HTTPException(status_code=400, detail="A customer with this phone or email already exists.")

    # Update the fields if provided
    if customer.name is not None:
        db_customer.name = customer.name
    if customer.phone is not None:
        db_customer.phone = customer.phone
    if customer.email is not None:
        db_customer.email = customer.email
    if customer.address is not None:
        db_customer.address = customer.address

    # Commit the changes to the database
    try:
        db.commit()
        db.refresh(db_customer)
    except Exception:
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the customer.")
    
    return db_customer

def delete_customer(db: Session, customer_id: int):
    # Fetch the customer record from the database
    db_customer = get_customer(db, customer_id)
    
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    try:
        # Delete the customer record
        db.delete(db_customer)
        db.commit()
    except Exception:
        db.rollback()  # Rollback in case of any error during deletion
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the customer.")

    return db_customer

def get_bills(db: Session, customer_name: Optional[str] = None, page: int = 1, limit: int = 10):
    query = db.query(Bill)

    # If there's a customer name search term, filter bills based on it (case-insensitive search on customer's name)
    if customer_name:
        query = query.join(Customer).filter(func.lower(Customer.name).like(f"%{customer_name.lower()}%"))

    # Apply pagination
    skip = (page - 1) * limit
    bills = query.offset(skip).limit(limit).all()

    return bills  

def get_bill(db: Session, bill_id: int):
    return db.query(Bill).filter(Bill.id == bill_id).first()    

def create_bill(db: Session, bill_data: BillCreateNested):
    with db.begin():
        # Create or get customer
        customer_data = bill_data.customer
        existing_customer = db.query(Customer).filter(
            (func.lower(Customer.phone) == func.lower(customer_data.phone)) |
            (func.lower(Customer.email) == func.lower(customer_data.email))
        ).first()

        if existing_customer:
            db_customer = existing_customer
        else:
            db_customer = Customer(**customer_data.dict())
            db.add(db_customer)
            db.flush()  # Get ID without full commit

        # Create bill
        bill = Bill(
            customer_id=db_customer.id,
            total_amount=bill_data.bill.total_amount,
            date=bill_data.bill.date,
            payment_mode=bill_data.bill.payment_mode
        )
        db.add(bill)
        db.flush()

        # Create bill items
        db.add_all([
            BillItem(
                bill_id=bill.id,
                medicine_id=item.medicine_id,
                quantity=item.quantity,
                price=item.price
            )
            for item in bill_data.bill_items
        ])

    db.refresh(bill)
    return bill


def update_bill(db: Session, bill_id: int, bill: BillUpdate):
    db_bill = get_bill(db, bill_id)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found.")
    if bill.customer_id is not None:
        db_bill.customer_id = bill.customer_id
    if bill.total_amount is not None:
        db_bill.total_amount = bill.total_amount
    if bill.date is not None:
        db_bill.date = bill.date
    if bill.payment_mode is not None:
        db_bill.payment_mode = bill.payment_mode
    try:
        db.commit()
        db.refresh(db_bill)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the bill.")
    return db_bill

def delete_bill(db: Session, bill_id: int):
    db_bill = get_bill(db, bill_id)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found.")
    try:
        db.delete(db_bill)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the bill.")
    return db_bill

def get_bill_items(db: Session, page: int = 1, limit: int = 10):
    query = db.query(BillItem)

    # Apply pagination
    skip = (page - 1) * limit
    bill_items = query.offset(skip).limit(limit).all()

    return bill_items

def get_bill_item(db: Session, bill_item_id: int):
    return db.query(BillItem).filter(BillItem.id == bill_item_id).first()   

def create_bill_item(db: Session, bill_item: BillItemCreate):
    db_bill_item = BillItem(
        bill_id=bill_item.bill_id,
        medicine_id=bill_item.medicine_id,
        quantity=bill_item.quantity,
        price=bill_item.price
    )

    try:
        db.add(db_bill_item)
        db.commit()
        db.refresh(db_bill_item)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while saving the bill item.")
    return db_bill_item

def update_bill_item(db: Session, bill_item_id: int, bill_item: BillItemUpdate):
    db_bill_item = get_bill_item(db, bill_item_id)
    if not db_bill_item:
        raise HTTPException(status_code=404, detail="Bill item not found.")
    if bill_item.bill_id is not None:
        db_bill_item.bill_id = bill_item.bill_id
    if bill_item.medicine_id is not None:
        db_bill_item.medicine_id = bill_item.medicine_id
    if bill_item.quantity is not None:
        db_bill_item.quantity = bill_item.quantity
    if bill_item.price is not None:
        db_bill_item.price = bill_item.price
    try:
        db.commit()
        db.refresh(db_bill_item)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the bill item.")
    return db_bill_item

def delete_bill_item(db: Session, bill_item_id: int):
    db_bill_item = get_bill_item(db, bill_item_id)
    if not db_bill_item:
        raise HTTPException(status_code=404, detail="Bill item not found.")
    try:
        db.delete(db_bill_item)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the bill item.")
    return db_bill_item

def get_bill_items_by_bill(db: Session, bill_id: int):
    return db.query(BillItem).filter(BillItem.bill_id == bill_id).all()

def get_bills_by_customer(db: Session, customer_id: int):
    return db.query(Bill).filter(Bill.customer_id == customer_id).all() 

def get_medicines_by_ids(db: Session, medicine_ids: List[int]):
    return db.query(Medicine).filter(Medicine.id.in_(medicine_ids)).all()

def get_customers_by_ids(db: Session, customer_ids: List[int]):
    return db.query(Customer).filter(Customer.id.in_(customer_ids)).all()


