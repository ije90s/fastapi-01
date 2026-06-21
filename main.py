from fastapi import FastAPI, HTTPException
import nanoid
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

type ItemId = str

class ItemColor(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'

class ItemBase(BaseModel):
    name: str = Field(description="상품명")
    color: Optional[ItemColor] = Field(default=None, description="상품 색상")
    #color: ItemColor | None = None

class Item(ItemBase):
    id: ItemId = Field(..., description="상품 ID")
    

temp_items = {
    "qRhBXnpry7": Item(id="qRhBXnpry7", name='아이템1', color=ItemColor.red),
    "cOPAmgTBfc": Item(id="cOPAmgTBfc", name="아이템2", color=ItemColor.green)
}

def item_or_404(item_id: ItemId) -> Item:
    if item_id not in temp_items:
        raise HTTPException(status_code=404, detail="아이템이 없어요")
    return temp_items[item_id]


@app.get("/items/{item_id}")
def read_item(item_id: ItemId) -> Item:
    return item_or_404(item_id)

@app.post("/items", status_code=201, summary="상품 등록")
def create_item(item: ItemBase):
    item_id = nanoid.generate(size=10)
    if item_id in temp_items:
        raise HTTPException(status_code=400, detail="아이템이 이미 있어요")
    #temp_items[item_id] = Item(id=item_id, name=item.name, color=item.color)
    temp_items[item_id] = Item(id=item_id, **item.model_dump())
    return temp_items[item_id]

@app.put("/items/{item_id}", status_code=202)
def update_item(item_id: ItemId, item: ItemBase) -> Item:
    _ = item_or_404(item_id)
    updated_item = Item(id=item_id, **item.model_dump())
    temp_items[item_id] = update_item
    return update_item

@app.delete('/items/{item_id}', status_code=204)
def delete_item(item_id: ItemId):
    _ = item_or_404(item_id)
    del temp_items[item_id]
    return {"deleted": True}