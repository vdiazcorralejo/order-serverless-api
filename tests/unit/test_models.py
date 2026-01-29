"""
Unit tests for Order models.

Tests domain models without any AWS dependencies.
"""
import pytest
from datetime import datetime
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from orders.models import Order, OrderStatus, OrderItem


class TestOrderStatus:
    """Test OrderStatus enum."""

    def test_order_status_values(self):
        """Test all order status values exist."""
        assert OrderStatus.PENDING == "PENDING"
        assert OrderStatus.CONFIRMED == "CONFIRMED"
        assert OrderStatus.PROCESSING == "PROCESSING"
        assert OrderStatus.SHIPPED == "SHIPPED"
        assert OrderStatus.DELIVERED == "DELIVERED"
        assert OrderStatus.CANCELLED == "CANCELLED"


class TestOrderItem:
    """Test OrderItem model."""

    def test_order_item_creation(self):
        """Test creating a valid order item."""
        item = OrderItem(
            product_id="prod-123",
            quantity=2,
            price=Decimal("29.99")
        )

        assert item.product_id == "prod-123"
        assert item.quantity == 2
        assert item.price == Decimal("29.99")

    def test_order_item_to_dict(self):
        """Test order item serialization."""
        item = OrderItem(
            product_id="prod-123",
            quantity=2,
            price=Decimal("29.99")
        )

        item_dict = item.to_dict()

        assert item_dict["product_id"] == "prod-123"
        assert item_dict["quantity"] == 2
        assert item_dict["price"] == 29.99  # Converted to float

    def test_order_item_from_dict(self):
        """Test order item deserialization."""
        data = {
            "product_id": "prod-123",
            "quantity": 2,
            "price": 29.99
        }

        item = OrderItem.from_dict(data)

        assert item.product_id == "prod-123"
        assert item.quantity == 2
        assert item.price == Decimal("29.99")


class TestOrder:
    """Test Order model."""

    def test_order_creation_valid(self):
        """Test creating a valid order."""
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING
        )

        assert order.order_id == "order-123"
        assert order.customer_id == "customer-456"
        assert order.total_amount == Decimal("59.98")
        assert order.status == OrderStatus.PENDING
        assert order.items == []
        assert isinstance(order.created_at, datetime)
        assert isinstance(order.updated_at, datetime)

    def test_order_with_items(self):
        """Test order with items."""
        items = [
            OrderItem("prod-1", 2, Decimal("29.99")),
            OrderItem("prod-2", 1, Decimal("49.99"))
        ]

        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("109.97"),
            status=OrderStatus.PENDING,
            items=items
        )

        assert len(order.items) == 2
        assert order.items[0].product_id == "prod-1"
        assert order.items[1].quantity == 1

    def test_order_negative_amount_fails(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="total_amount must be non-negative"):
            Order(
                order_id="order-123",
                customer_id="customer-456",
                total_amount=Decimal("-10.00"),
                status=OrderStatus.PENDING
            )

    def test_order_invalid_status_fails(self):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError, match="status must be a valid OrderStatus"):
            Order(
                order_id="order-123",
                customer_id="customer-456",
                total_amount=Decimal("59.98"),
                status="INVALID_STATUS"
            )

    def test_order_to_dict(self):
        """Test order serialization."""
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING,
            items=[OrderItem("prod-1", 2, Decimal("29.99"))]
        )

        order_dict = order.to_dict()

        assert order_dict["order_id"] == "order-123"
        assert order_dict["customer_id"] == "customer-456"
        assert order_dict["total_amount"] == 59.98
        assert order_dict["status"] == "PENDING"
        assert len(order_dict["items"]) == 1
        assert isinstance(order_dict["created_at"], str)
        assert isinstance(order_dict["updated_at"], str)

    def test_order_from_dict(self):
        """Test order deserialization."""
        data = {
            "order_id": "order-123",
            "customer_id": "customer-456",
            "total_amount": 59.98,
            "status": "PENDING",
            "items": [
                {"product_id": "prod-1", "quantity": 2, "price": 29.99}
            ],
            "created_at": "2026-01-29T12:00:00",
            "updated_at": "2026-01-29T12:00:00"
        }

        order = Order.from_dict(data)

        assert order.order_id == "order-123"
        assert order.customer_id == "customer-456"
        assert order.total_amount == Decimal("59.98")
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 1
        assert isinstance(order.created_at, datetime)

    def test_order_update_status(self):
        """Test updating order status."""
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING
        )

        original_updated = order.updated_at

        # Wait a bit and update
        import time
        time.sleep(0.01)

        order.status = OrderStatus.CONFIRMED
        order.updated_at = datetime.utcnow()

        assert order.status == OrderStatus.CONFIRMED
        assert order.updated_at > original_updated

    def test_order_empty_customer_id_fails(self):
        """Test that empty customer_id raises error."""
        with pytest.raises(ValueError, match="customer_id cannot be empty"):
            Order(
                order_id="order-123",
                customer_id="",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )

    def test_order_empty_order_id_fails(self):
        """Test that empty order_id raises error."""
        with pytest.raises(ValueError, match="order_id cannot be empty"):
            Order(
                order_id="",
                customer_id="customer-456",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )
