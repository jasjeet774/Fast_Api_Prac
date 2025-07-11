from fastapi import FastAPI ,HTTPException
from pydantic import BaseModel
#Creates your API application
app=FastAPI()

#This is a route decorator that says: when someone sends a GET request to /, run the function below.
@app.get("/")
def root():
    return {"message":"welcome to fastapi "}

@app.get("/hello/{name}")
def say_hello(name:str):
    return {"message": f"hello , {name}"}    

@app.get("/info/{name}")
def user_info(name:str,age:int=18):
    return {"name":name,"age":age}

class Item(BaseModel):
    name:str
    description: str | None=None
    price: float
    tax: float |None=None

# A list to store items
items = []

@app.post("/items/")
def create_item(item: Item):
    items.append(item)  # Store in memory
    return {"message": "Item added successfully!"}

@app.get("/items/")
def get_items():
    return items  # Return all stored items

@app.put('/items/{item_id}')
def update_item(item_id:int, updated_item:Item):
    if item_id>=len(items):
        raise HTTPException(status_code=404,detail="item not found")
    items[item_id]=updated_item
    return {"message": "Item updated successfully!"}

@app.delete('/items/{item_id}')
def delete_item(item_id:int):
    if item_id>=len(items):
        raise HTTPException(status_code=404,detail="item not found")
    deleted_items=items.pop(item_id)
    return {"message": "Item deleted successfully!", "item":deleted_items}