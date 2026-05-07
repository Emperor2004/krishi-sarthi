"""Test business logic and core functionality."""
import pytest
from datetime import datetime
from src.krishi.database import UserCRUD, InventoryCRUD, UdharCRUD, PendingUdharCRUD
from src.krishi.services.udhar_agent import create_udhar, pay_udhar
from src.krishi.services.listing_agent import extract_product


class TestUdharBusinessLogic:
    """Test udhar (credit) business logic."""
    
    def test_create_udhar_success(self, db_session, sample_vendor_data):
        """Test successful udhar creation."""
        # Create vendor first
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Create udhar
        result = create_udhar(
            vendor_id=vendor.id,
            consumer_name="Test Consumer",
            amount=500.0
        )
        
        assert result["success"] is True
        assert "transaction_id" in result
        assert "entry" in result
        assert result["entry"]["amount"] == 500.0
        assert result["entry"]["status"] == "pending"
    
    def test_create_udhar_invalid_amount(self, db_session, sample_vendor_data):
        """Test udhar creation with invalid amount."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        result = create_udhar(
            vendor_id=vendor.id,
            consumer_name="Test Consumer",
            amount=0.0  # Invalid amount
        )
        
        assert result["success"] is False
        assert "Amount must be greater than 0" in result["message"]
    
    def test_create_udhar_nonexistent_vendor(self, db_session):
        """Test udhar creation with nonexistent vendor."""
        result = create_udhar(
            vendor_id=999,
            consumer_name="Test Consumer",
            amount=500.0
        )
        
        assert result["success"] is False
        assert "Vendor ID 999 not found" in result["message"]
    
    def test_pay_udhar_full_payment(self, db_session, sample_vendor_data):
        """Test full udhar payment."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Create udhar first
        create_result = create_udhar(
            vendor_id=vendor.id,
            consumer_name="Test Consumer",
            amount=500.0
        )
        txn_id = create_result["transaction_id"]
        
        # Pay full amount
        pay_result = pay_udhar(txn_id, 500.0)
        
        assert pay_result["success"] is True
        assert "paid" in pay_result["message"].lower()
    
    def test_pay_udhar_partial_payment(self, db_session, sample_vendor_data):
        """Test partial udhar payment."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Create udhar first
        create_result = create_udhar(
            vendor_id=vendor.id,
            consumer_name="Test Consumer",
            amount=500.0
        )
        txn_id = create_result["transaction_id"]
        
        # Pay partial amount
        pay_result = pay_udhar(txn_id, 200.0)
        
        assert pay_result["success"] is True
        assert "partial" in pay_result["message"].lower()
        assert pay_result["entry"]["amount_due"] == 300.0


class TestInventoryBusinessLogic:
    """Test inventory management business logic."""
    
    def test_add_inventory_item_success(self, db_session, sample_vendor_data, sample_inventory_data):
        """Test successful inventory item addition."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Add vendor_id to inventory data
        inventory_data = {**sample_inventory_data, "vendor_id": vendor.id}
        item = InventoryCRUD.create_item(db_session, inventory_data)
        
        assert item.id is not None
        assert item.vendor_id == vendor.id
        assert item.product_name == "Tomatoes"
        assert item.price == 40.0
        assert item.quantity == 50.0
    
    def test_search_inventory_by_keywords(self, db_session, sample_vendor_data, sample_inventory_data):
        """Test inventory search functionality."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Add inventory items
        inventory_data = {**sample_inventory_data, "vendor_id": vendor.id}
        InventoryCRUD.create_item(db_session, inventory_data)
        
        # Search by keyword
        results = InventoryCRUD.search_inventory(db_session, ["tomato"])
        
        assert len(results) > 0
        assert "tomato" in results[0].product_name.lower()
    
    def test_get_vendor_inventory(self, db_session, sample_vendor_data, sample_inventory_data):
        """Test getting vendor's inventory."""
        vendor = UserCRUD.create_user(db_session, sample_vendor_data)
        
        # Add inventory items
        inventory_data = {**sample_inventory_data, "vendor_id": vendor.id}
        InventoryCRUD.create_item(db_session, inventory_data)
        
        # Get vendor inventory
        vendor_items = InventoryCRUD.get_vendor_inventory(db_session, vendor.id)
        
        assert len(vendor_items) == 1
        assert vendor_items[0].vendor_id == vendor.id


class TestListingAgent:
    """Test product listing agent functionality."""
    
    def test_extract_product_basic(self):
        """Test basic product extraction from text."""
        text = "50 kilo tomatoes 40 rupaye kilo"
        result = extract_product(text)
        
        assert result["product"] == "Tomatoes"
        assert result["quantity"] == 50.0
        assert result["unit"] == "kg"
        assert result["price"] == 40.0
        assert "freshness" in result
    
    def test_extract_product_with_freshness(self):
        """Test product extraction with freshness indicator."""
        text = "25 kilo fresh potatoes 30 rupaye kilo"
        result = extract_product(text)
        
        assert result["product"] == "Potatoes"
        assert result["quantity"] == 25.0
        assert result["unit"] == "kg"
        assert result["price"] == 30.0
        # Freshness should be higher for "fresh" keyword
        assert result["freshness"] >= 4
    
    def test_extract_product_complex_text(self):
        """Test product extraction from complex natural language."""
        text = "maine 15 dozen anda 5 rupaye piece mein bechna hai"
        result = extract_product(text)
        
        assert "egg" in result["product"].lower() or "anda" in result["product"].lower()
        assert result["quantity"] == 15.0
        assert result["unit"] == "dozen"
        assert result["price"] == 5.0
