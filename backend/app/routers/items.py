from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import db

router = APIRouter(prefix="/items", tags=["items"])


class ItemCreate(BaseModel):
    title: str
    description: str = ""


class ItemUpdate(BaseModel):
    title: str = None
    description: str = None
    status: str = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str


@router.get("", response_model=List[ItemResponse])
def list_items() -> List[Dict[str, Any]]:
    """获取所有 items"""
    rows = db.list_items()
    return [
        {
            "id": r["id"],
            "title": r["title"],
            "description": r["description"] or "",
            "status": r["status"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate) -> Dict[str, Any]:
    """创建新 item"""
    title = item.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    
    item_id = db.insert_item(title, item.description)
    row = db.get_item(item_id)
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"] or "",
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int) -> Dict[str, Any]:
    """获取单个 item"""
    row = db.get_item(item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="item not found")
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"] or "",
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate) -> Dict[str, Any]:
    """更新 item"""
    existing = db.get_item(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="item not found")
    
    update_data = item.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="no fields to update")
    
    db.update_item(item_id, update_data)
    row = db.get_item(item_id)
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"] or "",
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    """删除 item"""
    existing = db.get_item(item_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="item not found")
    db.delete_item(item_id)
