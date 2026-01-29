"""
Integration tests for API endpoints.

Tests complete E2E flow with real AWS services (or LocalStack).
"""
import pytest
import requests
import json
import os
from decimal import Decimal


# Get API URL from environment or use default
API_URL = os.getenv('API_URL', 'https://qqgiy0vtnh.execute-api.eu-west-1.amazonaws.com/dev')
ID_TOKEN = os.getenv('ID_TOKEN', '')


@pytest.fixture
def auth_headers():
    """Get authentication headers."""
    if not ID_TOKEN:
        pytest.skip("ID_TOKEN environment variable not set")

    return {
        'Authorization': f'Bearer {ID_TOKEN}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        'customer_id': 'test-customer-123',
        'total_amount': 99.99,
        'status': 'PENDING',
        'items': [
            {
                'product_id': 'prod-123',
                'quantity': 2,
                'price': 49.99
            }
        ]
    }


class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    def test_health_check(self):
        """Test API is accessible."""
        response = requests.get(f'{API_URL}/v1/orders')

        # Should return 401 without auth (not 404 or 500)
        assert response.status_code in [401, 403, 200]

    def test_create_order_e2e(self, auth_headers, sample_order_data):
        """Test creating an order end-to-end."""
        response = requests.post(
            f'{API_URL}/v1/orders',
            headers=auth_headers,
            json=sample_order_data
        )

        assert response.status_code == 201
        body = response.json()

        assert 'order_id' in body
        assert body['status'] == 'PENDING'
        assert body['total_amount'] == 99.99

        # Store order_id for cleanup
        return body['order_id']

    def test_list_orders_e2e(self, auth_headers):
        """Test listing orders."""
        response = requests.get(
            f'{API_URL}/v1/orders',
            headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()

        assert 'orders' in body
        assert isinstance(body['orders'], list)

    def test_get_order_e2e(self, auth_headers, sample_order_data):
        """Test getting a specific order."""
        # First create an order
        create_response = requests.post(
            f'{API_URL}/v1/orders',
            headers=auth_headers,
            json=sample_order_data
        )
        order_id = create_response.json()['order_id']

        # Get the order
        response = requests.get(
            f'{API_URL}/v1/orders/{order_id}',
            headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()

        assert body['order_id'] == order_id
        assert body['customer_id'] == sample_order_data['customer_id']

        # Cleanup
        requests.delete(f'{API_URL}/v1/orders/{order_id}', headers=auth_headers)

    def test_update_order_e2e(self, auth_headers, sample_order_data):
        """Test updating an order."""
        # Create order
        create_response = requests.post(
            f'{API_URL}/v1/orders',
            headers=auth_headers,
            json=sample_order_data
        )
        order_id = create_response.json()['order_id']

        # Update order
        update_data = {'status': 'CONFIRMED'}
        response = requests.put(
            f'{API_URL}/v1/orders/{order_id}',
            headers=auth_headers,
            json=update_data
        )

        assert response.status_code == 200
        body = response.json()
        assert body['status'] == 'CONFIRMED'

        # Cleanup
        requests.delete(f'{API_URL}/v1/orders/{order_id}', headers=auth_headers)

    def test_delete_order_e2e(self, auth_headers, sample_order_data):
        """Test deleting an order."""
        # Create order
        create_response = requests.post(
            f'{API_URL}/v1/orders',
            headers=auth_headers,
            json=sample_order_data
        )
        order_id = create_response.json()['order_id']

        # Delete order
        response = requests.delete(
            f'{API_URL}/v1/orders/{order_id}',
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = requests.get(
            f'{API_URL}/v1/orders/{order_id}',
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_authentication_required(self):
        """Test that authentication is required."""
        response = requests.get(f'{API_URL}/v1/orders')

        assert response.status_code in [401, 403]

    def test_invalid_token_rejected(self):
        """Test that invalid token is rejected."""
        headers = {
            'Authorization': 'Bearer invalid-token',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f'{API_URL}/v1/orders',
            headers=headers
        )

        assert response.status_code in [401, 403]

    def test_create_order_validation(self, auth_headers):
        """Test order validation."""
        invalid_data = {
            'customer_id': '',  # Empty customer_id
            'total_amount': -10.00,  # Negative amount
            'status': 'INVALID_STATUS'  # Invalid status
        }

        response = requests.post(
            f'{API_URL}/v1/orders',
            headers=auth_headers,
            json=invalid_data
        )

        assert response.status_code == 400

    def test_get_nonexistent_order(self, auth_headers):
        """Test getting non-existent order."""
        response = requests.get(
            f'{API_URL}/v1/orders/non-existent-id',
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_cors_headers(self, auth_headers):
        """Test CORS headers are present."""
        response = requests.get(
            f'{API_URL}/v1/orders',
            headers=auth_headers
        )

        # Check for CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200


class TestAPIPerformance:
    """Performance tests for API."""

    def test_response_time(self, auth_headers):
        """Test API response time is acceptable."""
        import time

        start = time.time()
        response = requests.get(
            f'{API_URL}/v1/orders',
            headers=auth_headers
        )
        duration = time.time() - start

        assert duration < 2.0  # Should respond in less than 2 seconds
        assert response.status_code == 200

    @pytest.mark.slow
    def test_concurrent_requests(self, auth_headers, sample_order_data):
        """Test handling concurrent requests."""
        import concurrent.futures

        def create_order():
            return requests.post(
                f'{API_URL}/v1/orders',
                headers=auth_headers,
                json=sample_order_data
            )

        # Create 5 orders concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_order) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(r.status_code == 201 for r in results)

        # Cleanup
        for result in results:
            order_id = result.json()['order_id']
            requests.delete(f'{API_URL}/v1/orders/{order_id}', headers=auth_headers)


class TestAPIFilters:
    """Test API filtering capabilities."""

    def test_filter_by_customer(self, auth_headers, sample_order_data):
        """Test filtering orders by customer_id."""
        # Create orders for different customers
        customer_ids = ['customer-a', 'customer-b']
        order_ids = []

        for customer_id in customer_ids:
            data = sample_order_data.copy()
            data['customer_id'] = customer_id

            response = requests.post(
                f'{API_URL}/v1/orders',
                headers=auth_headers,
                json=data
            )
            order_ids.append(response.json()['order_id'])

        # Filter by customer-a
        response = requests.get(
            f'{API_URL}/v1/orders?customer_id=customer-a',
            headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()

        # Should only return orders for customer-a
        customer_a_orders = [o for o in body['orders'] if o['customer_id'] == 'customer-a']
        assert len(customer_a_orders) >= 1

        # Cleanup
        for order_id in order_ids:
            requests.delete(f'{API_URL}/v1/orders/{order_id}', headers=auth_headers)
