#!/usr/bin/env python3
"""
Initialize Demo Data
Script to seed the demo database with sample data for demonstrations
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.krishi.database import init_database, get_db, UserCRUD, InventoryCRUD, UdharCRUD
from src.krishi.security import SecurityManager
from src.krishi.logging import app_logger


class DemoDataSeeder:
    """Seed demo database with sample data"""
    
    def __init__(self):
        self.logger = app_logger
        self.data_dir = Path(__file__).parent.parent / "data"
        
    def load_sample_data(self):
        """Load sample data from JSON files"""
        try:
            with open(self.data_dir / "sample_vendors.json", 'r', encoding='utf-8') as f:
                vendors = json.load(f)
            
            with open(self.data_dir / "sample_consumers.json", 'r', encoding='utf-8') as f:
                consumers = json.load(f)
            
            self.logger.info(f"Loaded {len(vendors)} vendors and {len(consumers)} consumers")
            return vendors, consumers
            
        except Exception as e:
            self.logger.error(f"Failed to load sample data: {e}")
            return [], []
    
    def create_demo_database(self):
        """Create and initialize demo database"""
        try:
            # Initialize database schema
            init_database()
            self.logger.info("Database schema initialized")
            
            # Get database session
            db = next(get_db())
            
            # Load sample data
            vendors, consumers = self.load_sample_data()
            
            # Clear existing data (for demo)
            self.clear_demo_data(db)
            
            # Seed vendors
            for vendor_data in vendors:
                self.create_vendor(db, vendor_data)
            
            # Seed consumers
            for consumer_data in consumers:
                self.create_consumer(db, consumer_data)
            
            # Create some sample orders and udhar transactions
            self.create_sample_business_data(db, vendors, consumers)
            
            db.commit()
            self.logger.info("Demo data seeded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create demo database: {e}")
            return False
    
    def clear_demo_data(self, db):
        """Clear existing demo data"""
        try:
            # Clear tables in correct order to respect foreign keys
            db.execute("DELETE FROM udhar_transactions")
            db.execute("DELETE FROM orders")
            db.execute("DELETE FROM inventory")
            db.execute("DELETE FROM users")
            db.commit()
            self.logger.info("Cleared existing demo data")
        except Exception as e:
            self.logger.error(f"Failed to clear demo data: {e}")
    
    def create_vendor(self, db, vendor_data):
        """Create vendor with hashed password"""
        try:
            # Hash password
            vendor_data["password_hash"] = SecurityManager.get_password_hash(vendor_data["password"])
            vendor_data["is_active"] = True
            vendor_data["created_at"] = datetime.utcnow()
            
            # Remove password field (don't store plain text)
            vendor_data.pop("password", None)
            
            # Extract products for later
            products = vendor_data.pop("products", [])
            
            # Create user
            user = UserCRUD.create_user(db, vendor_data)
            
            # Create inventory items
            for product in products:
                inventory_data = {
                    "vendor_id": user.id,
                    "product_name": product["product_name"],
                    "price": product["price"],
                    "unit": product["unit"],
                    "quantity": product["quantity"],
                    "freshness": product["freshness"],
                    "timestamp": datetime.fromisoformat(product["timestamp"].replace('Z', '+00:00'))
                }
                InventoryCRUD.create_item(db, inventory_data)
            
            self.logger.info(f"Created vendor: {vendor_data['name']} with {len(products)} products")
            
        except Exception as e:
            self.logger.error(f"Failed to create vendor {vendor_data.get('name', 'Unknown')}: {e}")
    
    def create_consumer(self, db, consumer_data):
        """Create consumer with hashed password"""
        try:
            # Hash password
            consumer_data["password_hash"] = SecurityManager.get_password_hash(consumer_data["password"])
            consumer_data["is_active"] = True
            consumer_data["created_at"] = datetime.utcnow()
            
            # Remove password field
            consumer_data.pop("password", None)
            
            # Create user
            user = UserCRUD.create_user(db, consumer_data)
            
            self.logger.info(f"Created consumer: {consumer_data['name']}")
            
        except Exception as e:
            self.logger.error(f"Failed to create consumer {consumer_data.get('name', 'Unknown')}: {e}")
    
    def create_sample_business_data(self, db, vendors, consumers):
        """Create sample orders and udhar transactions"""
        try:
            # Create sample udhar transactions
            sample_udhar = [
                {
                    "vendor_id": vendors[0]["id"],
                    "vendor_name": vendors[0]["name"],
                    "consumer_name": consumers[0]["name"],
                    "amount": 500.0,
                    "original_amount": 500.0,
                    "amount_due": 500.0,
                    "status": "pending"
                },
                {
                    "vendor_id": vendors[1]["id"],
                    "vendor_name": vendors[1]["name"],
                    "consumer_name": consumers[1]["name"],
                    "amount": 300.0,
                    "original_amount": 300.0,
                    "amount_due": 300.0,
                    "status": "pending"
                }
            ]
            
            for udhar_data in sample_udhar:
                # Create transaction ID
                import uuid
                udhar_data["id"] = "U" + str(uuid.uuid4())[:6].upper()
                udhar_data["timestamp"] = datetime.utcnow()
                udhar_data["audit_log"] = [
                    {
                        "action": "CREATE",
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": f"Demo: {udhar_data['vendor_name']} ne {udhar_data['consumer_name']} ko ₹{udhar_data['amount']} ka udhar diya."
                    }
                ]
                
                UdharCRUD.create_transaction(db, udhar_data)
            
            self.logger.info(f"Created {len(sample_udhar)} sample udhar transactions")
            
        except Exception as e:
            self.logger.error(f"Failed to create sample business data: {e}")
    
    def verify_demo_data(self):
        """Verify demo data was created correctly"""
        try:
            db = next(get_db())
            
            # Count users
            from src.krishi.database.models import User
            vendor_count = db.query(User).filter(User.role == "vendor").count()
            consumer_count = db.query(User).filter(User.role == "consumer").count()
            
            # Count inventory items
            from src.krishi.database.models import Inventory
            inventory_count = db.query(Inventory).count()
            
            # Count udhar transactions
            from src.krishi.database.models import UdharTransaction
            udhar_count = db.query(UdharTransaction).count()
            
            self.logger.info("=== Demo Data Verification ===")
            self.logger.info(f"Vendors: {vendor_count}")
            self.logger.info(f"Consumers: {consumer_count}")
            self.logger.info(f"Inventory Items: {inventory_count}")
            self.logger.info(f"Udhar Transactions: {udhar_count}")
            
            # Expected counts
            expected_vendors = 3
            expected_consumers = 3
            expected_inventory = 9  # 3 vendors × 3 products each
            expected_udhar = 2
            
            success = (
                vendor_count == expected_vendors and
                consumer_count == expected_consumers and
                inventory_count == expected_inventory and
                udhar_count == expected_udhar
            )
            
            if success:
                self.logger.info("✓ All demo data verified successfully")
                return True
            else:
                self.logger.warning("✗ Demo data verification failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to verify demo data: {e}")
            return False
    
    def create_demo_database_file(self):
        """Create SQLite database file directly for demo"""
        try:
            db_path = Path(__file__).parent.parent / "demo.db"
            
            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create tables (simplified version)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    address TEXT,
                    shop_name TEXT,
                    location TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    unit TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    freshness INTEGER DEFAULT 3,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vendor_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS udhar_transactions (
                    id TEXT PRIMARY KEY,
                    vendor_id INTEGER NOT NULL,
                    vendor_name TEXT NOT NULL,
                    consumer_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    original_amount REAL NOT NULL,
                    amount_due REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    audit_log TEXT DEFAULT '[]',
                    FOREIGN KEY (vendor_id) REFERENCES users (id)
                )
            ''')
            
            # Load and insert data
            vendors, consumers = self.load_sample_data()
            
            # Insert vendors
            for vendor in vendors:
                vendor_hash = SecurityManager.get_password_hash(vendor["password"])
                cursor.execute('''
                    INSERT INTO users (phone, name, role, password_hash, address, shop_name, location, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vendor["phone"],
                    vendor["name"],
                    vendor["role"],
                    vendor_hash,
                    vendor["address"],
                    vendor["shop_name"],
                    json.dumps(vendor["location"]),
                    1,
                    datetime.fromisoformat(vendor["created_at"].replace('Z', '+00:00'))
                ))
                
                vendor_id = cursor.lastrowid
                
                # Insert inventory
                for product in vendor["products"]:
                    cursor.execute('''
                        INSERT INTO inventory (vendor_id, product_name, price, unit, quantity, freshness, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        vendor_id,
                        product["product_name"],
                        product["price"],
                        product["unit"],
                        product["quantity"],
                        product["freshness"],
                        datetime.fromisoformat(product["timestamp"].replace('Z', '+00:00'))
                    ))
            
            # Insert consumers
            for consumer in consumers:
                consumer_hash = SecurityManager.get_password_hash(consumer["password"])
                cursor.execute('''
                    INSERT INTO users (phone, name, role, password_hash, address, location, is_active, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    consumer["phone"],
                    consumer["name"],
                    consumer["role"],
                    consumer_hash,
                    consumer["address"],
                    json.dumps(consumer["location"]),
                    1,
                    datetime.fromisoformat(consumer["created_at"].replace('Z', '+00:00'))
                ))
            
            # Insert sample udhar transactions
            sample_udhar = [
                {
                    "id": "UDEMO001",
                    "vendor_id": vendors[0]["id"],
                    "vendor_name": vendors[0]["name"],
                    "consumer_name": consumers[0]["name"],
                    "amount": 500.0,
                    "original_amount": 500.0,
                    "amount_due": 500.0,
                    "status": "pending",
                    "audit_log": json.dumps([{
                        "action": "CREATE",
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": f"Demo: {vendors[0]['name']} ne {consumers[0]['name']} ko ₹500 ka udhar diya."
                    }])
                }
            ]
            
            for udhar in sample_udhar:
                cursor.execute('''
                    INSERT INTO udhar_transactions (id, vendor_id, vendor_name, consumer_name, amount, original_amount, amount_due, status, timestamp, audit_log)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    udhar["id"],
                    udhar["vendor_id"],
                    udhar["vendor_name"],
                    udhar["consumer_name"],
                    udhar["amount"],
                    udhar["original_amount"],
                    udhar["amount_due"],
                    udhar["status"],
                    datetime.utcnow(),
                    udhar["audit_log"]
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Demo database created at: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create demo database: {e}")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize demo data for Krishi Saarthi")
    parser.add_argument("--force", action="store_true", help="Force recreate demo data")
    parser.add_argument("--verify", action="store_true", help="Verify demo data only")
    parser.add_argument("--sqlite", action="store_true", help="Create SQLite database file directly")
    
    args = parser.parse_args()
    
    seeder = DemoDataSeeder()
    
    if args.verify:
        # Only verify existing data
        success = seeder.verify_demo_data()
        sys.exit(0 if success else 1)
    
    elif args.sqlite:
        # Create SQLite database directly
        success = seeder.create_demo_database_file()
        sys.exit(0 if success else 1)
    
    else:
        # Use ORM to create demo data
        success = seeder.create_demo_database()
        
        if success:
            # Verify the data
            verification = seeder.verify_demo_data()
            sys.exit(0 if verification else 1)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
