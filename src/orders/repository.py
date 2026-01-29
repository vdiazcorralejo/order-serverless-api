import os
import boto3
from boto3.dynamodb.conditions import Key
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import logging

try:
    from orders.models import Order, OrderStatus
except ImportError:
    # For Lambda execution environment
    from models import Order, OrderStatus

logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class OrderRepository:
    """DynamoDB repository for orders"""

    def __init__(self, table_name: Optional[str] = None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE')
        if not self.table_name:
            raise ValueError("table_name must be provided or DYNAMODB_TABLE environment variable must be set")
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"Initialized OrderRepository with table: {self.table_name}")

    def create_order(self, order: Order) -> Order:
        """Create a new order"""
        try:
            item = {
                'order_id': order.order_id,
                'customer_id': order.customer_id,
                'status': order.status.value,
                'total_amount': Decimal(str(order.total_amount)),
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'items': order.items
            }

            self.table.put_item(Item=item)
            logger.info(f"Created order: {order.order_id}")
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            response = self.table.get_item(Key={'order_id': order_id})

            if 'Item' not in response:
                logger.warning(f"Order not found: {order_id}")
                return None

            item = response['Item']
            order = Order.from_dict({
                'order_id': item['order_id'],
                'customer_id': item['customer_id'],
                'status': item['status'],
                'total_amount': float(item['total_amount']),
                'created_at': item['created_at'],
                'updated_at': item.get('updated_at'),
                'items': item.get('items', [])
            })

            logger.info(f"Retrieved order: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            raise

    def list_orders(self, customer_id: Optional[str] = None, limit: int = 50) -> List[Order]:
        """List orders, optionally filtered by customer"""
        try:
            if customer_id:
                # Query by customer using GSI
                response = self.table.query(
                    IndexName='CustomerIndex',
                    KeyConditionExpression=Key('customer_id').eq(customer_id),
                    Limit=limit,
                    ScanIndexForward=False  # Most recent first
                )
            else:
                # Scan all orders (use with caution in production)
                response = self.table.scan(Limit=limit)

            orders = []
            for item in response.get('Items', []):
                order = Order.from_dict({
                    'order_id': item['order_id'],
                    'customer_id': item['customer_id'],
                    'status': item['status'],
                    'total_amount': float(item['total_amount']),
                    'created_at': item['created_at'],
                    'updated_at': item.get('updated_at'),
                    'items': item.get('items', [])
                })
                orders.append(order)

            logger.info(f"Listed {len(orders)} orders")
            return orders
        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            raise

    def update_order(self, order_id: str, updates: dict) -> Optional[Order]:
        """Update an order"""
        try:
            # Build update expression
            update_expr = "SET "
            expr_attr_values = {}
            expr_attr_names = {}

            for key, value in updates.items():
                if key in ['status', 'total_amount', 'items']:
                    placeholder = f"#{key}"
                    value_placeholder = f":{key}"
                    expr_attr_names[placeholder] = key

                    if key == 'total_amount':
                        expr_attr_values[value_placeholder] = Decimal(str(value))
                    else:
                        expr_attr_values[value_placeholder] = value

                    update_expr += f"{placeholder} = {value_placeholder}, "

            # Add updated_at timestamp
            update_expr += "#updated_at = :updated_at"
            expr_attr_names["#updated_at"] = "updated_at"
            expr_attr_values[":updated_at"] = datetime.utcnow().isoformat()

            response = self.table.update_item(
                Key={'order_id': order_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues='ALL_NEW'
            )

            item = response['Attributes']
            order = Order.from_dict({
                'order_id': item['order_id'],
                'customer_id': item['customer_id'],
                'status': item['status'],
                'total_amount': float(item['total_amount']),
                'created_at': item['created_at'],
                'updated_at': item.get('updated_at'),
                'items': item.get('items', [])
            })

            logger.info(f"Updated order: {order_id}")
            return order
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            raise

    def delete_order(self, order_id: str) -> bool:
        """Delete an order"""
        try:
            self.table.delete_item(Key={'order_id': order_id})
            logger.info(f"Deleted order: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting order: {str(e)}")
            raise
