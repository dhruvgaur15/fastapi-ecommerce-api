from app import models
from app.dependencies.auth import role_checker
from app.dependencies.common import current_user_dependency, db_dependency
from app.schemas import ProductBase
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/product", tags=["Products"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_checker("admin"))],
)
async def add_product(product: ProductBase, db: db_dependency):
    db_product = models.Product(**product.model_dump())

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("", status_code=status.HTTP_200_OK)
def get_products(db: db_dependency):
    products = db.query(models.Product).all()
    return products


@router.get("{id}")
def get_product(product_id: int, db: db_dependency):
    print(type(db))
    print(type(models.Product))
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        return {"message": "product not found"}
    return product


@router.put("", dependencies=[Depends(role_checker("admin"))])
def update_product(id: int, db: db_dependency, productData: ProductBase):
    print(id)
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if product:
        product.name = productData.name
        product.price = productData.price
        product.quantity = productData.quantity

        db.commit()
        db.refresh(product)
        return product

    return {"message": "product not found"}


@router.delete("")
def delete_product(
    product_id: int, db: db_dependency, current_user: current_user_dependency
):

    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    print(product)
    if product is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )

    order_items = (
        db.query(models.OrderItems)
        .filter(models.OrderItems.product_id == product_id)
        .all()
    )
    try:
        for order_item in order_items:
            remaining_orders = (
                db.query(models.OrderItems)
                .filter(
                    models.OrderItems.order_id == order_item.order_id,
                    models.OrderItems.id != order_item.id,
                )
                .count()
            )

            order = None
            if remaining_orders == 0:
                order = (
                    db.query(models.Orders)
                    .filter(models.Orders.id == order_item.order_id)
                    .first()
                )

            db.delete(order_item)

            if order:
                db.delete(order)

        db.delete(product)
        db.commit()
        return "Product deleted successfully."

    except Exception:
        db.rollback()

        raise
