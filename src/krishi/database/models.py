"""Database models for Krishi Saarthi using SQLAlchemy."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # vendor, consumer
    password_hash = Column(String(255), nullable=False)
    address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Vendor-specific fields
    shop_name = Column(String(100))
    location = Column(JSON)  # {"lat": 0.0, "lng": 0.0}
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="vendor")
    orders_as_vendor = relationship("Order", foreign_keys="Order.vendor_id", back_populates="vendor")
    udhar_transactions = relationship("UdharTransaction", back_populates="vendor")


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # kg, gram, piece, etc.
    quantity = Column(Float, nullable=False)
    freshness = Column(Integer, default=3)  # 1-5 scale
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("User", back_populates="inventory_items")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    consumer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String(100), nullable=False)
    unit = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    consumer_address = Column(Text)
    status = Column(String(20), default="pending")  # pending, confirmed, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    consumer = relationship("User", foreign_keys=[consumer_id])
    vendor = relationship("User", foreign_keys=[vendor_id], back_populates="orders_as_vendor")


class UdharTransaction(Base):
    __tablename__ = "udhar_transactions"
    
    id = Column(String(20), primary_key=True)  # Transaction ID like "UABC123"
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_name = Column(String(100), nullable=False)
    consumer_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    original_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, partial, paid
    timestamp = Column(DateTime, default=datetime.utcnow)
    audit_log = Column(JSON, default=list)
    
    # Relationships
    vendor = relationship("User", back_populates="udhar_transactions")


class PendingUdhar(Base):
    __tablename__ = "pending_udhar"
    
    id = Column(String(50), primary_key=True)  # PU timestamp
    vendor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consumer_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="awaiting_consumer")  # awaiting_consumer, confirmed, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    voice_confirmation = Column(String(10))  # haan, nahin
    confirmed_at = Column(DateTime)
    rejected_at = Column(DateTime)
