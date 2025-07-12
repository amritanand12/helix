from typing import Optional
from pydantic import BaseModel

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
