from enum import Enum

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class UserRoles(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CUSTOMER = "customer"


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="customer", nullable=False)

    orders = relationship("Orders", back_populates="user")
