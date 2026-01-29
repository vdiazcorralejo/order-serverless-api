import json
import os
import logging
from datetime import datetime
from decimal import Decimal
import uuid
from typing import Dict, Any

try:
    from orders.models import Order, OrderStatus
    from orders.repository import OrderRepository
except ImportError:
    # For Lambda execution environment
    from models import Order, OrderStatus
    from repository import OrderRepository

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Repository will be initialized on first use
_repository = None


def get_repository():
    """Get or create repository instance (lazy initialization)"""
    global _repository
    if _repository is None:
        _repository = OrderRepository()
    return _repository


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for Orders API
    Handles all CRUD operations based on HTTP method and path
    """
    logger.info(f"Received event: {json.dumps(event)}")

    # Get repository instance
    repository = get_repository()

    try:
        http_method = event['httpMethod']
        path = event['path']
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}

        # Get customer_id from JWT claims
        customer_id = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            claims = event['requestContext']['authorizer'].get('claims', {})
            customer_id = claims.get('sub')  # Cognito user ID

        # Route to appropriate handler
        if path == '/v1/orders':
            if http_method == 'POST':
                return handle_create_order(event, customer_id)
            elif http_method == 'GET':
                return handle_list_orders(event, query_parameters)
            else:
                return error_response(405, "Method not allowed")

        elif path.startswith('/v1/orders/'):
            order_id = path_parameters.get('id')
            if not order_id:
                return error_response(400, "Order ID is required")

            if http_method == 'GET':
                return handle_get_order(order_id)
            elif http_method == 'PUT':
                return handle_update_order(order_id, event)
            elif http_method == 'DELETE':
                return handle_delete_order(order_id)
            else:
                return error_response(405, "Method not allowed")

        return error_response(404, "Endpoint not found")

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


def handle_create_order(event: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
    """Handle POST /v1/orders"""
    repository = get_repository()
    try:
        body = json.loads(event.get('body', '{}'))

        # Generate order ID
        order_id = str(uuid.uuid4())

        # Validate required fields
        if 'total_amount' not in body:
            return error_response(400, "Missing required field: total_amount")

        # Use authenticated customer_id or from body
        customer_id = customer_id or body.get('customer_id')
        if not customer_id:
            return error_response(400, "customer_id is required")

        # Create order object
        order = Order(
            order_id=order_id,
            customer_id=customer_id,
            status=OrderStatus(body.get('status', 'PENDING')),
            total_amount=Decimal(str(body.get('total_amount', 0))),
            created_at=datetime.utcnow().isoformat(),
            items=body.get('items', [])
        )

        # Validate order
        errors = order.validate()
        if errors:
            return error_response(400, f"Validation errors: {', '.join(errors)}")

        # Save to DynamoDB
        created_order = repository.create_order(order)

        logger.info(f"Order created: {order_id}")
        return success_response(201, created_order.to_dict())

    except ValueError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return error_response(500, "Failed to create order")


def handle_get_order(order_id: str) -> Dict[str, Any]:
    """Handle GET /v1/orders/{id}"""
    repository = get_repository()
    try:
        order = repository.get_order(order_id)

        if not order:
            return error_response(404, "Order not found")

        return success_response(200, order.to_dict())

    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return error_response(500, "Failed to get order")


def handle_list_orders(event: Dict[str, Any], query_params: Dict[str, str]) -> Dict[str, Any]:
    """Handle GET /v1/orders"""
    repository = get_repository()
    try:
        customer_id = query_params.get('customer_id')
        limit = int(query_params.get('limit', 50))

        orders = repository.list_orders(customer_id=customer_id, limit=limit)

        return success_response(200, {
            'orders': [order.to_dict() for order in orders],
            'count': len(orders)
        })

    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        return error_response(500, "Failed to list orders")


def handle_update_order(order_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PUT /v1/orders/{id}"""
    repository = get_repository()
    try:
        body = json.loads(event.get('body', '{}'))

        # Check if order exists
        existing_order = repository.get_order(order_id)
        if not existing_order:
            return error_response(404, "Order not found")

        # Update order fields
        if 'status' in body:
            existing_order.status = OrderStatus(body['status'])
        if 'total_amount' in body:
            existing_order.total_amount = Decimal(str(body['total_amount']))
        if 'items' in body:
            existing_order.items = body['items']

        # Update timestamp
        existing_order.updated_at = datetime.utcnow()

        # Save updated order
        updated_order = repository.update_order(existing_order)

        logger.info(f"Order updated: {order_id}")
        return success_response(200, updated_order.to_dict())

    except ValueError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        return error_response(500, "Failed to update order")


def handle_delete_order(order_id: str) -> Dict[str, Any]:
    """Handle DELETE /v1/orders/{id}"""
    repository = get_repository()
    try:
        # Check if order exists
        existing_order = repository.get_order(order_id)
        if not existing_order:
            return error_response(404, "Order not found")

        # Delete order
        repository.delete_order(order_id)

        logger.info(f"Order deleted: {order_id}")
        return {
            'statusCode': 204,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': ''
        }

    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}")
        return error_response(500, "Failed to delete order")


def success_response(status_code: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a successful API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Build an error API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }
