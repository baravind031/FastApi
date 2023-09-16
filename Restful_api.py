import uvicorn
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
logger = logging.getLogger(__name__)
# MongoDB Configuration
MONGODB_URL = "mongodb+srv://RESTful_api:kX0RKb08N7iNQ2YT@cluster0.uejwn03.mongodb.net/"  
DATABASE_NAME = "RestAPI_DataBase"
COLLECTION_NAME = "store"

# MongoDB Connection
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Pydantic Model for Item
class Item(BaseModel):
    name: str
    description: str
    Mail_id:str

# Create an item
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    item_dict = item.dict()
    result = await collection.insert_one(item_dict)
    item_dict["_id"] = str(result.inserted_id)
    return item_dict

# Get all items
@app.get("/items/", response_model=list[Item])
async def get_all_items():
    items = []
    async for item in collection.find():
        items.append(Item(**item))
    return items

# Get a single item by ID

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    logger.info(f"Attempting to find item with ID: {item_id}")
    item = await collection.find_one({"_id": item_id})
    if item is None:
        logger.warning(f"Item with ID {item_id} not found")
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info(f"Found item: {item}")
    return Item(**item)


# Update an item by ID
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    existing_item = await collection.find_one({"_id": item_id})
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.dict(exclude_unset=True)
    updated_item = {**existing_item, **update_data}
    
    await collection.replace_one({"_id": item_id}, updated_item)
    return Item(**updated_item)

# Delete an item by ID
@app.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: str):
     
    item = await collection.find_one({"_id": item_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await collection.delete_one({"_id": item_id})
    return Item(**item)

if __name__ == "__main__":
   
    uvicorn.run(app, host="0.0.0.0", port=8000)
