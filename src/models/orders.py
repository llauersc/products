from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrderStatusEnum(StrEnum):
    ADDED = "ADDED"
    UPDATED = "UPDATED"


class OrderDB(BaseModel):
    id: UUID
    client_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime


class OrderItemDB(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime


class ProductDB(BaseModel):
    id: UUID
    name: str
    quantity: int
    price: float
    category_id: UUID
    created_at: datetime


class ClientDB(BaseModel):
    id: UUID
    name: str
    address: str
    created_at: datetime


class CategoryDB(BaseModel):
    id: UUID
    name: str
    parent_id: UUID
    created_at: datetime


class AddItemToOrderRequest(BaseModel):
    product_id: UUID = Field(..., description="ID товара")
    quantity: int = Field(..., gt=0, description="Количество товара")


class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    created_at: datetime


class AddItemToOrderResponse(BaseModel):
    message: str
    order_item: OrderItemResponse
    remaining_stock: int


class ClientOrderTotalResponse(BaseModel):
    client_name: str
    total_amount: float


class CategoryChildCountResponse(BaseModel):
    category_name: str
    child_count: int


class TopProductResponse(BaseModel):
    product_name: str
    top_level_category: Optional[str]
    total_sold: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class AddItemResult(BaseModel):
    action: str  # "added" или "updated"
    order_item: dict  # сырые данные из БД
    remaining_stock: int
