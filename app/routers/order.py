from fastapi import APIRouter, HTTPException, status

from app import models
from app.dependencies.common import current_user_dependency, db_dependency
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def createOrder(
    order: OrderCreate, db: db_dependency, curre_user: current_user_dependency
):
    total_amount = 0

    new_order = models.Orders(user_id=curre_user.id, status="pending", total_amount=0)

    db.add(new_order)
    db.flush()

    for item in order.items:
        product = (
            db.query(models.Product)
            .filter(models.Product.id == item.product_id)
            .first()
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient quantity for product {product.id}",
            )

        item_total = product.price * item.quantity
        total_amount += item_total

        order_item = models.OrderItems(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price,
        )

        db.add(order_item)

        product.quantity -= item.quantity

    new_order.total_amount = total_amount

    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
def getOrders(db: db_dependency, current_user: current_user_dependency):

    if current_user.role == "admin":
        orders = db.query(models.Orders).all()
    else:
        orders = (
            db.query(models.Orders)
            .filter(models.Orders.user_id == current_user.id)
            .all()
        )

    return orders


@router.get("/{id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def getOrderById(id: int, db: db_dependency, current_user: current_user_dependency):

    query = db.query(models.Orders).filter(models.Orders.id == id)

    if current_user.role != "admin":
        query = query.filter(models.Orders.user_id == current_user.id)

    order = query.first()

    return order


@router.put("/{id}", status_code=status.HTTP_200_OK)
def updateOrder(
    id: int,
    order_update: OrderUpdate,
    db: db_dependency,
    current_user: current_user_dependency,
):
    order = db.query(models.Orders).filter(models.Orders.id == id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if current_user.role != "admin" and current_user.id != order.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with {current_user.id} cannot modify this order",
        )

    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled.",
        )

    if order_update.status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order can only be cancelled",
        )

    order.status = order_update.status

    order_items = (
        db.query(models.OrderItems).filter(models.OrderItems.order_id == id).all()
    )

    for item in order_items:
        product = (
            db.query(models.Product)
            .filter(models.Product.id == item.product_id)
            .first()
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="product not found."
            )

        product.quantity += item.quantity

    db.commit()
    db.refresh(order)

    return order


@router.delete("", status_code=status.HTTP_200_OK)
def deleteOrder(
    order_id: int, db: db_dependency, current_user: current_user_dependency
):
    order = db.query(models.Orders).filter(models.Orders.id == order_id).first()
    print(order, order_id)

    if not order:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if current_user.role != "admin" and current_user.id != order.user_id:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions."
        )

    try:
        order_items = (
            db.query(models.OrderItems)
            .filter(models.OrderItems.order_id == order.id)
            .all()
        )

        for order_item in order_items:
            product = (
                db.query(models.Product)
                .filter(models.Product.id == order_item.product_id)
                .first()
            )

            if product:
                product.quantity += order_item.quantity

        db.delete(order_item)

        db.commit()

    except Exception:
        db.rollback()
        raise
