from enum import Enum
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"  # Keep for backward compatibility


class OrderItem:
    """Order item model"""

    def __init__(self, product_id: str, quantity: int, price: Decimal):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def to_dict(self) -> dict:
        """Convert item to dictionary"""
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": float(self.price)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'OrderItem':
        """Create item from dictionary"""
        return cls(
            product_id=data["product_id"],
            quantity=data["quantity"],
            price=Decimal(str(data["price"]))
        )


class Order:
    """Order domain model"""

    def __init__(
        self,
        order_id: str,
        customer_id: str,
        total_amount: Decimal,
        status: OrderStatus,
        items: Optional[List[OrderItem]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        # Validation
        if not order_id:
            raise ValueError("order_id cannot be empty")
        if not customer_id:
            raise ValueError("customer_id cannot be empty")
        if total_amount < 0:
            raise ValueError("total_amount must be non-negative")
        if not isinstance(status, OrderStatus):
            raise ValueError("status must be a valid OrderStatus")

        self.order_id = order_id
        self.customer_id = customer_id
        self.total_amount = total_amount
        self.status = status
        self.items = items or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> dict:
        """Convert order to dictionary"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status.value if isinstance(self.status, OrderStatus) else self.status,
            "total_amount": float(self.total_amount),
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "items": [item.to_dict() if isinstance(item, OrderItem) else item for item in self.items]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Create order from dictionary"""
        items_data = data.get("items", [])
        items = []
        for item in items_data:
            if isinstance(item, dict):
                items.append(OrderItem.from_dict(item))
            elif isinstance(item, OrderItem):
                items.append(item)

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        return cls(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            total_amount=Decimal(str(data["total_amount"])),
            status=OrderStatus(data["status"]),
            items=items,
            created_at=created_at,
            updated_at=updated_at
        )

    def validate(self) -> list[str]:
        """Validate order data"""
        errors = []

        if not self.order_id:
            errors.append("order_id is required")

        if not self.customer_id:
            errors.append("customer_id is required")

        if self.total_amount <= 0:
            errors.append("total_amount must be greater than 0")

        if not self.status:
            errors.append("status is required")

        return errors
