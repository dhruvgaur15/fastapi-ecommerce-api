from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50))
    price = Column(Float)
    quantity = Column(Integer)

    order_items = relationship("OrderItems", back_populates="product")
