"""
Unit tests for OrderRepository.

Uses moto to mock DynamoDB operations.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from moto import mock_dynamodb
import boto3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from orders.repository import OrderRepository
from orders.models import Order, OrderStatus, OrderItem


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb():
        # Create mock DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        # Create table
        table = dynamodb.create_table(
            TableName='test-orders-table',
            KeySchema=[
                {'AttributeName': 'order_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'order_id', 'AttributeType': 'S'},
                {'AttributeName': 'customer_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'CustomerIndex',
                    'KeySchema': [
                        {'AttributeName': 'customer_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        yield table


@pytest.fixture
def repository(dynamodb_table):
    """Create OrderRepository instance with mock table."""
    return OrderRepository(table_name='test-orders-table')


class TestOrderRepository:
    """Test OrderRepository operations."""

    def test_create_order_success(self, repository):
        """Test creating an order."""
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING,
            items=[OrderItem("prod-1", 2, Decimal("29.99"))]
        )

        result = repository.create_order(order)

        assert result is True

    def test_get_order_found(self, repository):
        """Test getting an existing order."""
        # Create order first
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING
        )
        repository.create_order(order)

        # Get order
        retrieved = repository.get_order("order-123")

        assert retrieved is not None
        assert retrieved.order_id == "order-123"
        assert retrieved.customer_id == "customer-456"
        assert retrieved.total_amount == Decimal("59.98")

    def test_get_order_not_found(self, repository):
        """Test getting non-existent order returns None."""
        result = repository.get_order("non-existent-id")

        assert result is None

    def test_update_order_success(self, repository):
        """Test updating an order."""
        # Create order
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING
        )
        repository.create_order(order)

        # Update order
        order.status = OrderStatus.CONFIRMED
        order.updated_at = datetime.utcnow()

        result = repository.update_order(order)

        assert result is True

        # Verify update
        updated = repository.get_order("order-123")
        assert updated.status == OrderStatus.CONFIRMED

    def test_delete_order_success(self, repository):
        """Test deleting an order."""
        # Create order
        order = Order(
            order_id="order-123",
            customer_id="customer-456",
            total_amount=Decimal("59.98"),
            status=OrderStatus.PENDING
        )
        repository.create_order(order)

        # Delete order
        result = repository.delete_order("order-123")

        assert result is True

        # Verify deletion
        deleted = repository.get_order("order-123")
        assert deleted is None

    def test_list_orders(self, repository):
        """Test listing all orders."""
        # Create multiple orders
        for i in range(3):
            order = Order(
                order_id=f"order-{i}",
                customer_id="customer-456",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )
            repository.create_order(order)

        # List orders
        orders = repository.list_orders()

        assert len(orders) == 3
        assert all(isinstance(o, Order) for o in orders)

    def test_list_orders_with_limit(self, repository):
        """Test listing orders with limit."""
        # Create multiple orders
        for i in range(5):
            order = Order(
                order_id=f"order-{i}",
                customer_id="customer-456",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )
            repository.create_order(order)

        # List with limit
        orders = repository.list_orders(limit=2)

        assert len(orders) <= 2

    def test_get_orders_by_customer(self, repository):
        """Test getting orders by customer ID."""
        # Create orders for different customers
        for i in range(2):
            order = Order(
                order_id=f"order-a-{i}",
                customer_id="customer-aaa",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )
            repository.create_order(order)

        for i in range(3):
            order = Order(
                order_id=f"order-b-{i}",
                customer_id="customer-bbb",
                total_amount=Decimal("59.98"),
                status=OrderStatus.PENDING
            )
            repository.create_order(order)

        # Get orders for customer-aaa
        orders = repository.get_orders_by_customer("customer-aaa")

        assert len(orders) == 2
        assert all(o.customer_id == "customer-aaa" for o in orders)

    def test_create_order_with_items(self, repository):
        """Test creating order with multiple items."""
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

        repository.create_order(order)

        # Verify items are stored
        retrieved = repository.get_order("order-123")
        assert len(retrieved.items) == 2
        assert retrieved.items[0].product_id == "prod-1"
        assert retrieved.items[1].quantity == 1
