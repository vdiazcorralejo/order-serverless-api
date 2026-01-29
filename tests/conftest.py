"""
Shared pytest fixtures and configuration.
"""
import pytest
import os
import sys

# Add src to path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


@pytest.fixture(scope='session')
def aws_credentials():
    """Mock AWS credentials for testing."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


@pytest.fixture(scope='session')
def dynamodb_table_name():
    """DynamoDB table name for testing."""
    return 'test-orders-table'


@pytest.fixture
def sample_order_id():
    """Generate a unique order ID."""
    import uuid
    return f"order-{uuid.uuid4()}"


@pytest.fixture
def sample_customer_id():
    """Generate a unique customer ID."""
    import uuid
    return f"customer-{uuid.uuid4()}"
