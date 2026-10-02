from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

# এটি হলো ডাটাবেসের টেবিল তৈরি করার আসল কোড
class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float)
    is_available = Column(Boolean, default=True)