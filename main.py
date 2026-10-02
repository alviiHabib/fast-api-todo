from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import schemas

# Instructs the engine to create tables in PostgreSQL if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ORM to FastAPI Walkthrough")

@app.post("/items", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_payload: schemas.ItemCreate, 
    db: Session = Depends(get_db)
):
    """
    Creates a new database record.
    """
    # 1. Unpack validated Pydantic data into the SQLAlchemy model
    new_item = models.Item(**item_payload.model_dump())

    # 2. Add object to the session's pending transaction
    db.add(new_item)

    # 3. Commit the transaction (executes INSERT in PostgreSQL)
    db.commit()

    # 4. Refresh the Python object to pull back generated fields (like auto-increment ID)
    db.refresh(new_item)

    # 5. Return the ORM object (Pydantic serializes it to JSON)
    return new_item


@app.get("/items/{item_id}", response_model=schemas.ItemResponse)
def get_item(
    item_id: int, 
    db: Session = Depends(get_db)
):
    """
    Fetches an item by primary key.
    """
    # Translates directly to a SELECT ... WHERE id = item_id query
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with id {item_id} not found"
        )
    return item

@app.get("/items", response_model=List[schemas.ItemResponse])
def get_all_items(db: Session = Depends(get_db)):
    """
    Fetches all items from the database.
    """
    # এখানে Todo এর বদলে Item হবে
    return db.query(models.Item).all()

@app.get("/")
def home():
    return {"message": "Welcome to To-Do App Backend!"}

# ==========================================
# UPDATE OPERATION (PUT)
# ==========================================
@app.put("/items/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, item_payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    
    # ১. প্রথমে ডাটাবেস থেকে ওই নির্দিষ্ট ID-এর ডেটাটি খুঁজে বের করা
    # এখানে .first() এর আগে filter ঠিকমতো কাজ করছে কি না তা নিশ্চিত করার জন্য id এর টাইপ কাস্টিং করা হলো
    item_query = db.query(models.Item).filter(models.Item.id == item_id)
    item = item_query.first()
    
    # যদি ওই ID-এর কোনো ডেটা না থাকে, তবে 404 Error দেখাবে
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with id {item_id} not found"
        )
    
    # ২. পুরনো ডেটাগুলোকে ইউজারের দেওয়া নতুন ডেটা দিয়ে আপডেট করা
    # dictionary আকারে ডেটা আপডেট করা বেশি নিরাপদ
    update_data = item_payload.model_dump(exclude_unset=True) 
    
    for key, value in update_data.items():
        setattr(item, key, value)
    
    # ৩. ডাটাবেসে নতুন পরিবর্তনগুলো সেভ (Commit) করা
    db.commit()
    db.refresh(item)
    
    return item

# ==========================================
# DELETE OPERATION (DELETE)
# ==========================================
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    # ১. প্রথমে ডাটাবেস থেকে ওই নির্দিষ্ট ID-এর ডেটাটি খুঁজে বের করা
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    
    # যদি ওই ID-এর কোনো ডেটা না থাকে, তবে 404 Error দেখাবে
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with id {item_id} not found"
        )
    
    # ২. ডাটাবেস থেকে ডেটাটি ডিলিট করে দেওয়া
    db.delete(item)
    db.commit()
    
    return None    