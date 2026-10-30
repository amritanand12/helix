from typing import Optional, List
from pydantic import BaseModel

# Medicine Schemas
class MedicineBase(BaseModel):
    name: str
    price: float

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class MedicineOut(MedicineBase):
    id: int

    class Config:
        orm_mode = True

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerOut(CustomerBase):
    id: int

    class Config:
        orm_mode = True

# Bill Item Schemas
class BillItemBase(BaseModel):
    bill_id: int
    medicine_id: int
    quantity: int
    price: float

class BillItemCreate(BillItemBase):
    pass

class BillItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None  
    
class BillItemOut(BillItemBase):
    id: int

    class Config:
        orm_mode = True

# Bill Schemas
class BillBase(BaseModel):
    total_amount: float
    payment_mode: str
    date: str
    customer_id: int

class BillCreate(BillBase):
    pass

class BillUpdate(BaseModel):
    payment_mode: Optional[str] = None
    total_amount: Optional[float] = None

class BillOut(BillBase):
    id: int

    class Config:
        orm_mode = True

# Nested Bill Creation Schema for API
class BillCreateNested(BaseModel):
    bill: BillCreate
    customer: CustomerCreate
    bill_items: List[BillItemCreate]
