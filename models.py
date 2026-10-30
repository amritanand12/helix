from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from database import Base
from sqlalchemy.orm import relationship


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float)

    bill_items = relationship("BillItem", back_populates="medicine")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True)
    email = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)

    bills = relationship("Bill", back_populates="customer")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Float)
    date = Column(Date)
    payment_mode = Column(String)

    customer = relationship("Customer", back_populates="bills")
    items = relationship("BillItem", back_populates="bill")

class BillItem(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    quantity = Column(Integer)
    price = Column(Float)

    medicine = relationship("Medicine", back_populates="bill_items")
    bill = relationship("Bill", back_populates="items")