from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from database import Base
from datetime import datetime


# =========================================================
# USER MODEL
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )


# =========================================================
# FAVORITE FOOD MODEL
# =========================================================

class FavoriteFood(Base):

    __tablename__ = "favorite_foods"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    food_name = Column(
        String,
        nullable=False
    )


# =========================================================
# CART ITEM MODEL
# =========================================================

class CartItem(Base):

    __tablename__ = "cart_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    food_name = Column(
        String,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False,
        default=0
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )


# =========================================================
# ORDER MODEL
# =========================================================

class Order(Base):

    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    full_name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )

    address = Column(
        String,
        nullable=False
    )

    total = Column(
        Float,
        nullable=False,
        default=0
    )

    status = Column(
        String,
        nullable=False,
        default="Placed"
    )

    order_date = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# ORDER ITEM MODEL
# =========================================================

class OrderItem(Base):

    __tablename__ = "order_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    food_name = Column(
        String,
        nullable=False
    )

    price = Column(
        Float,
        nullable=False,
        default=0
    )

    quantity = Column(
        Integer,
        nullable=False,
        default=1
    )