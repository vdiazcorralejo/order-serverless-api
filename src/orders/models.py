from enum import Enum
from typing import Optional
from datetime import datetime
from decimal import Decimal


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Order:
    """Order domain model"""

    def __init__(
        self,
        order_id: str,
        customer_id: str,
        status: OrderStatus,
        total_amount: Decimal,
        created_at: str,
        updated_at: Optional[str] = None,
        items: Optional[list] = None
    ):
        self.order_id = order_id
        self.customer_id = customer_id
        self.status = status
        self.total_amount = total_amount
        self.created_at = created_at
        self.updated_at = updated_at or created_at
        self.items = items or []

    def to_dict(self) -> dict:
        """Convert order to dictionary"""
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status.value,
            "total_amount": float(self.total_amount),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Create order from dictionary"""
        return cls(
            order_id=data["order_id"],
            customer_id=data["customer_id"],
            status=OrderStatus(data["status"]),
            total_amount=Decimal(str(data["total_amount"])),
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
            items=data.get("items", [])
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
