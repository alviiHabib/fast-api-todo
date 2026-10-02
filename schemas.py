from typing import Optional
from pydantic import BaseModel, Field

# Base schema for shared attributes
class ItemBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    is_available: bool = True

# Schema for incoming POST requests (no ID required from client)
class ItemCreate(ItemBase):
    id: int

# Schema for outgoing HTTP responses (reads data from the ORM object)
class ItemResponse(ItemBase):
    id: int

    class Config:
        # Enables reading data directly from SQLAlchemy objects instead of just dicts
        from_attributes = True