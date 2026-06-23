from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from supabase import acreate_client, AsyncClient
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

supabase: AsyncClient

type ItemId = str


class ItemColor(str, Enum):
    red = "red"
    green = "green"
    blue = "blue"


class ItemBase(BaseModel):
    name: str = Field(description="상품명")
    color: Optional[ItemColor] = Field(default=None, description="상품 색상")


class Item(ItemBase):
    id: ItemId = Field(..., description="상품 ID")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global supabase
    supabase = await acreate_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )
    yield


app = FastAPI(lifespan=lifespan)


async def item_or_404(item_id: ItemId) -> Item:
    result = await supabase.table("items").select("*").eq("id", item_id).maybe_single().execute()
    if result is None or result.data is None:
        raise HTTPException(status_code=404, detail="아이템이 없어요")
    return Item(**result.data)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: ItemId) -> Item:
    return await item_or_404(item_id)


@app.post("/items", status_code=201, summary="상품 등록")
async def create_item(item: ItemBase) -> Item:
    result = await supabase.table("items").insert(item.model_dump(mode="json")).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="아이템 생성 실패")
    return Item(**result.data[0])


@app.put("/items/{item_id}", status_code=202)
async def update_item(item_id: ItemId, item: ItemBase) -> Item:
    await item_or_404(item_id)
    result = await supabase.table("items").update(item.model_dump(mode="json")).eq("id", item_id).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="아이템 수정 실패")
    return Item(**result.data[0])


@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: ItemId):
    await item_or_404(item_id)
    await supabase.table("items").delete().eq("id", item_id).execute()
