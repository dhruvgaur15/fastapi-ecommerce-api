from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrdersItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes: True


class OrderResponse(BaseModel):
    id: int
    status: str
    user_id: int
    total_amount: float
    items: list[OrdersItemResponse]

    class Config:
        from_attributes: True


class OrderUpdate(BaseModel):
    status: OrderStatus
