"""
Unit tests for Lambda handler.

Tests HTTP routing and business logic with mocked repository.
"""
import pytest
import json
from decimal import Decimal
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from orders.handler import lambda_handler
from orders.models import Order, OrderStatus, OrderItem


@pytest.fixture
def mock_repository():
    """Mock OrderRepository."""
    with patch('orders.handler.get_repository') as mock:
        repo_instance = Mock()
        mock.return_value = repo_instance
        yield repo_instance


@pytest.fixture
def api_context():
    """Mock Lambda context."""
    context = Mock()
    context.request_id = "test-request-id"
    return context


class TestHandlerPOST:
    """Test POST /v1/orders endpoint."""

    def test_post_orders_valid(self, mock_repository, api_context):
        """Test creating an order with valid data."""
        # Mock should return the order object, not True
        def create_order_side_effect(order):
            return order
        mock_repository.create_order.side_effect = create_order_side_effect

        event = {
            'httpMethod': 'POST',
            'path': '/v1/orders',
            'body': json.dumps({
                'customer_id': 'customer-123',
                'total_amount': 59.98,
                'status': 'PENDING',
                'items': [
                    {'product_id': 'prod-1', 'quantity': 2, 'price': 29.99}
                ]
            }),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'order_id' in body
        assert body['customer_id'] is not None
        assert body['status'] == 'PENDING'
        assert mock_repository.create_order.called

    def test_post_orders_invalid_json(self, mock_repository, api_context):
        """Test creating order with invalid JSON."""
        event = {
            'httpMethod': 'POST',
            'path': '/v1/orders',
            'body': 'invalid json',
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body

    def test_post_orders_missing_fields(self, mock_repository, api_context):
        """Test creating order with missing required fields."""
        event = {
            'httpMethod': 'POST',
            'path': '/v1/orders',
            'body': json.dumps({
                'total_amount': 59.98
                # Missing customer_id
            }),
            'requestContext': {}  # No auth so customer_id is required
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'customer_id is required' in body['error']

    def test_post_orders_negative_amount(self, mock_repository, api_context):
        """Test creating order with negative amount."""
        event = {
            'httpMethod': 'POST',
            'path': '/v1/orders',
            'body': json.dumps({
                'customer_id': 'customer-123',
                'total_amount': -10.00,
                'status': 'PENDING'
            }),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 400


class TestHandlerGET:
    """Test GET endpoints."""

    def test_get_orders_list(self, mock_repository, api_context):
        """Test listing all orders."""
        mock_orders = [
            Order("order-1", "customer-1", Decimal("59.98"), OrderStatus.PENDING),
            Order("order-2", "customer-2", Decimal("79.98"), OrderStatus.CONFIRMED)
        ]
        mock_repository.list_orders.return_value = mock_orders

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders',
            'queryStringParameters': None,
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'orders' in body
        assert len(body['orders']) == 2
        assert mock_repository.list_orders.called

    def test_get_orders_by_customer(self, mock_repository, api_context):
        """Test getting orders filtered by customer."""
        mock_orders = [
            Order("order-1", "customer-123", Decimal("59.98"), OrderStatus.PENDING)
        ]
        mock_repository.list_orders.return_value = mock_orders

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders',
            'queryStringParameters': {'customer_id': 'customer-123'},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['orders']) == 1
        assert body['orders'][0]['customer_id'] == 'customer-123'

    def test_get_order_by_id_found(self, mock_repository, api_context):
        """Test getting specific order by ID."""
        mock_order = Order(
            "order-123",
            "customer-456",
            Decimal("59.98"),
            OrderStatus.PENDING
        )
        mock_repository.get_order.return_value = mock_order

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders/order-123',
            'pathParameters': {'id': 'order-123'},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['order_id'] == 'order-123'
        mock_repository.get_order.assert_called_with('order-123')

    def test_get_order_by_id_not_found(self, mock_repository, api_context):
        """Test getting non-existent order."""
        mock_repository.get_order.return_value = None

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders/non-existent',
            'pathParameters': {'id': 'non-existent'},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body


class TestHandlerPUT:
    """Test PUT /v1/orders/{id} endpoint."""

    def test_put_order_success(self, mock_repository, api_context):
        """Test updating an order."""
        existing_order = Order(
            "order-123",
            "customer-456",
            Decimal("59.98"),
            OrderStatus.PENDING
        )
        mock_repository.get_order.return_value = existing_order

        # Mock update to return the order with updated status
        def update_side_effect(order):
            return order
        mock_repository.update_order.side_effect = update_side_effect

        event = {
            'httpMethod': 'PUT',
            'path': '/v1/orders/order-123',
            'pathParameters': {'id': 'order-123'},
            'body': json.dumps({
                'status': 'CONFIRMED'
            }),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'CONFIRMED'
        assert mock_repository.update_order.called

    def test_put_order_not_found(self, mock_repository, api_context):
        """Test updating non-existent order."""
        mock_repository.get_order.return_value = None

        event = {
            'httpMethod': 'PUT',
            'path': '/v1/orders/non-existent',
            'pathParameters': {'id': 'non-existent'},
            'body': json.dumps({'status': 'CONFIRMED'}),
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 404


class TestHandlerDELETE:
    """Test DELETE /v1/orders/{id} endpoint."""

    def test_delete_order_success(self, mock_repository, api_context):
        """Test deleting an order."""
        mock_repository.delete_order.return_value = True

        event = {
            'httpMethod': 'DELETE',
            'path': '/v1/orders/order-123',
            'pathParameters': {'id': 'order-123'},
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 204
        mock_repository.delete_order.assert_called_with('order-123')


class TestHandlerErrors:
    """Test error handling."""

    def test_invalid_http_method(self, mock_repository, api_context):
        """Test unsupported HTTP method."""
        event = {
            'httpMethod': 'PATCH',
            'path': '/v1/orders',
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 405

    def test_missing_authorization(self, mock_repository, api_context):
        """Test request without authorization - handler still processes but with no customer_id."""
        mock_repository.list_orders.return_value = []

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders',
            'queryStringParameters': None,
            'requestContext': {}
        }

        response = lambda_handler(event, api_context)

        # Handler processes request even without auth (API Gateway should handle auth)
        assert response['statusCode'] == 200
        assert mock_repository.list_orders.called

    def test_internal_server_error(self, mock_repository, api_context):
        """Test handling of unexpected errors."""
        mock_repository.list_orders.side_effect = Exception("Database error")

        event = {
            'httpMethod': 'GET',
            'path': '/v1/orders',
            'requestContext': {
                'authorizer': {
                    'claims': {'sub': 'user-123'}
                }
            }
        }

        response = lambda_handler(event, api_context)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
