from typing import Optional
from pydantic import BaseModel

class MedicineBase(BaseModel):
    name: str
    price: int

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None

class MedicineOut(MedicineBase):
    id: int

    class Config:
        orm_mode = True
