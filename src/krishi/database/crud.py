"""CRUD operations for database models."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import User, Inventory, Order, UdharTransaction, PendingUdhar


class UserCRUD:
    """CRUD operations for User model."""
    
    @staticmethod
    def create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
        """Get user by phone number."""
        return db.query(User).filter(User.phone == phone).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user information."""
        db.query(User).filter(User.id == user_id).update(updates)
        db.commit()
        return True


class InventoryCRUD:
    """CRUD operations for Inventory model."""
    
    @staticmethod
    def create_item(db: Session, item_data: Dict[str, Any]) -> Inventory:
        """Create a new inventory item."""
        db_item = Inventory(**item_data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_vendor_inventory(db: Session, vendor_id: int) -> List[Inventory]:
        """Get all inventory items for a vendor."""
        return db.query(Inventory).filter(Inventory.vendor_id == vendor_id).all()
    
    @staticmethod
    def search_inventory(db: Session, keywords: List[str], limit: int = 10) -> List[Inventory]:
        """Search inventory by keywords."""
        if not keywords:
            return db.query(Inventory).filter(Inventory.quantity > 0).limit(limit).all()
        
        conditions = []
        for keyword in keywords:
            conditions.append(Inventory.product_name.ilike(f"%{keyword}%"))
        
        return db.query(Inventory).filter(
            and_(Inventory.quantity > 0, or_(*conditions))
        ).limit(limit).all()


class OrderCRUD:
    """CRUD operations for Order model."""
    
    @staticmethod
    def create_order(db: Session, order_data: Dict[str, Any]) -> Order:
        """Create a new order."""
        db_order = Order(**order_data)
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    @staticmethod
    def get_vendor_orders(db: Session, vendor_id: int, limit: int = 50) -> List[Order]:
        """Get orders for a vendor."""
        return db.query(Order).filter(Order.vendor_id == vendor_id).order_by(
            Order.created_at.desc()
        ).limit(limit).all()


class UdharCRUD:
    """CRUD operations for UdharTransaction model."""
    
    @staticmethod
    def create_transaction(db: Session, txn_data: Dict[str, Any]) -> UdharTransaction:
        """Create a new udhar transaction."""
        db_txn = UdharTransaction(**txn_data)
        db.add(db_txn)
        db.commit()
        db.refresh(db_txn)
        return db_txn
    
    @staticmethod
    def update_transaction(db: Session, txn_id: str, updates: Dict[str, Any]) -> Optional[UdharTransaction]:
        """Update udhar transaction."""
        db_txn = db.query(UdharTransaction).filter(UdharTransaction.id == txn_id).first()
        if db_txn:
            for key, value in updates.items():
                setattr(db_txn, key, value)
            db.commit()
            db.refresh(db_txn)
        return db_txn
    
    @staticmethod
    def get_vendor_transactions(db: Session, vendor_id: int) -> List[UdharTransaction]:
        """Get all udhar transactions for a vendor."""
        return db.query(UdharTransaction).filter(
            UdharTransaction.vendor_id == vendor_id
        ).order_by(UdharTransaction.timestamp.desc()).all()
    
    @staticmethod
    def get_consumer_transactions(db: Session, consumer_name: str) -> List[UdharTransaction]:
        """Get udhar transactions for a consumer."""
        return db.query(UdharTransaction).filter(
            UdharTransaction.consumer_name.ilike(f"%{consumer_name}%")
        ).order_by(UdharTransaction.timestamp.desc()).all()


class PendingUdharCRUD:
    """CRUD operations for PendingUdhar model."""
    
    @staticmethod
    def create_pending(db: Session, pending_data: Dict[str, Any]) -> PendingUdhar:
        """Create a new pending udhar."""
        db_pending = PendingUdhar(**pending_data)
        db.add(db_pending)
        db.commit()
        db.refresh(db_pending)
        return db_pending
    
    @staticmethod
    def get_pending_for_consumer(db: Session, consumer_name: str) -> Optional[PendingUdhar]:
        """Get pending udhar for a specific consumer."""
        return db.query(PendingUdhar).filter(
            and_(
                PendingUdhar.consumer_name.ilike(f"%{consumer_name}%"),
                PendingUdhar.status == "awaiting_consumer"
            )
        ).first()
    
    @staticmethod
    def update_pending(db: Session, pending_id: str, updates: Dict[str, Any]) -> Optional[PendingUdhar]:
        """Update pending udhar."""
        db_pending = db.query(PendingUdhar).filter(PendingUdhar.id == pending_id).first()
        if db_pending:
            for key, value in updates.items():
                setattr(db_pending, key, value)
            db.commit()
            db.refresh(db_pending)
        return db_pending
