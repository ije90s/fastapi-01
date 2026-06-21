from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

class ItemColor(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'

class Item(BaseModel):
    id: int
    name: str = Field(description="상품명")
    color: Optional[ItemColor] = Field(default=None, description="상품 색상")
    #color: ItemColor | None = None

temp_items = {
    1: Item(id=1, name='아이템1', color=ItemColor.red),
    2: Item(id=2, name="아이템2", color=ItemColor.green)
}

@app.get("/items/{item_id}")
def read_item(item_id: int) -> Item:
    if item_id in temp_items:
        return temp_items[item_id]
    else:
        raise HTTPException(status_code=404, detail="아이템이 없어요");

@app.post("/items", status_code=201, summary="상품 등록")
def create_item(item: Item):
    if item.id in temp_items:
        raise HTTPException(status_code=400, detail="아이템이 이미 있어요")
    temp_items[item.id] = item
    return item