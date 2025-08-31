import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_user():
    """Mock user for testing"""
    user = MagicMock()
    user.id = 1
    user.username = 'testuser'
    user.email = 'test@example.com'
    user.first_name = 'Test'
    user.last_name = 'User'
    user.role = 'COMMON_USER'
    user.company = None
    user.is_active = True
    return user

@pytest.fixture
def mock_verification():
    """Mock email verification for testing"""
    verification = MagicMock()
    verification.token = 'test-token-123'
    verification.is_expired.return_value = False
    verification.is_verified = False
    return verification
