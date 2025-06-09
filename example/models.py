"""
Example SQLAlchemy models showing enum usage.
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"  # This will be detected as a new value


class OrderStatus(PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PROCESSING = "processing"  # New value 1
    SHIPPED = "shipped"
    DELIVERED = "delivered"    # New value 2


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    status = Column(Enum(UserStatus, name='user_status'))


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    status = Column(Enum(OrderStatus, name='order_status'))
    description = Column(String(200))