# from fastapi import FastAPI ,HTTPException
# from pydantic import BaseModel
# #Creates your API application
# app=FastAPI()

# #This is a route decorator that says: when someone sends a GET request to /, run the function below.
# @app.get("/")
# def root():
#     return {"message":"welcome to fastapi "}

# @app.get("/hello/{name}")
# def say_hello(name:str):
#     return {"message": f"hello , {name}"}    

# @app.get("/info/{name}")
# def user_info(name:str,age:int=18):
#     return {"name":name,"age":age}

# class Item(BaseModel):
#     name:str
#     description: str | None=None
#     price: float
#     tax: float |None=None

# # A list to store items
# items = []

# @app.post("/items/")
# def create_item(item: Item):
#     items.append(item)  # Store in memory
#     return {"message": "Item added successfully!"}

# @app.get("/items/")
# def get_items():
#     return items  # Return all stored items

# @app.put('/items/{item_id}')
# def update_item(item_id:int, updated_item:Item):
#     if item_id>=len(items):
#         raise HTTPException(status_code=404,detail="item not found")
#     items[item_id]=updated_item
#     return {"message": "Item updated successfully!"}

# @app.delete('/items/{item_id}')
# def delete_item(item_id:int):
#     if item_id>=len(items):
#         raise HTTPException(status_code=404,detail="item not found")
#     deleted_items=items.pop(item_id)
#     return {"message": "Item deleted successfully!", "item":deleted_items}


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import Base, engine, SessionLocal

app=FastAPI()

class ItemDB(Base):
    __tablename__="items"

    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    description=Column(String)
    price=Column(float)
    tax=Column(float)

Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()    

# FastAPI uses Pydantic to validate data sent by users (inputs) and data you send back (outputs).

#This class defines the shape of data that you expect in POST and PUT requests.
class ItemCreate(BaseModel):
    name:str
    description=str | None=None  
    price:float
    tax:float | None=None        

class ItemOut(ItemCreate):
    id:int

    class comfig:
        orm_mode=True    

# Create API routes

@app.post("/items/", response_model=ItemOut)
def create_item(item:ItemCreate,db: Session=Depends(get_db)):
    db_item=ItemDB(**item.model_dump() ) #convert pydantic to db model
    db.add(db_item)           #add to DB session
    db.commit()              # save to DB
    db.refresh(db_item)  # get updated data
    return db_item 
     
@app.get("/items/",response_model=list[ItemOut])
def get_items(db:Session=Depends(get_db)):
    return db.query(ItemDB).all()

@app.put("/items/{item_id}",response_model=ItemOut)
def update_item(item_id:int, item:ItemCreate,db:Session=Depends(get_db)):
    db_item=db.query(ItemDB).filter(ItemDB.id==item.db).first()
    if not db_item:
        raise HTTPException(status_code=404,detail="")
    for key , value in item.model_dump.items():
        setattr(db_item,key,value)
    db.commit()
    db.refresh(db_item)
    return db_item    

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}
