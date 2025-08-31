import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

class TestViews(TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    @patch('core.views.send_verification_email')
    @patch('core.models.CustomUser.objects.create_user')
    @patch('core.models.Company.objects.get_or_create')
    @patch('core.models.EmailVerification.objects.create')
    def test_register_user_success(self, mock_verification_create, mock_company_get, mock_user_create, mock_send_email):
        """Test successful user registration endpoint"""
        # Mock all database operations
        mock_company = MagicMock()
        mock_company_get.return_value = (mock_company, True)
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = 'newuser@example.com'
        mock_user_create.return_value = mock_user
        
        mock_verification = MagicMock()
        mock_verification_create.return_value = mock_verification
        
        # Mock email sending
        mock_send_email.return_value = None
        
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
            'company_name': 'New Company',
            'company_email': 'hr@newcompany.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        mock_user_create.assert_called_once()
        mock_send_email.assert_called_once()

    @patch('core.models.CustomUser.objects.filter')
    def test_register_user_duplicate_email(self, mock_user_filter):
        """Test registration endpoint with duplicate email"""
        # Mock user already exists
        mock_user_filter.return_value.exists.return_value = True
        
        url = reverse('register')
        data = {
            'username': 'duplicateuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Duplicate',
            'last_name': 'User',
            'company_name': 'Duplicate Company',
            'company_email': 'hr@duplicate.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('core.models.EmailVerification.objects.get')
    def test_verify_email_success(self, mock_verification_get):
        """Test successful email verification endpoint"""
        # Mock verification object
        mock_verification = MagicMock()
        mock_verification.user = MagicMock()
        mock_verification.user.is_active = False
        mock_verification_get.return_value = mock_verification
        
        url = reverse('verify_email')
        data = {'token': 'test-token-123'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_verification.user.save.assert_called_once()
        mock_verification.save.assert_called_once()

    @patch('core.models.EmailVerification.objects.get')
    def test_verify_email_invalid_token(self, mock_verification_get):
        """Test email verification endpoint with invalid token"""
        # Mock verification not found
        mock_verification_get.side_effect = Exception("Verification not found")
        
        url = reverse('verify_email')
        data = {'token': 'invalid-token'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('core.models.CustomUser.objects.get')
    @patch('core.views.RefreshToken.for_user')
    def test_login_user_success(self, mock_refresh_token, mock_user_get):
        """Test successful user login endpoint"""
        # Mock user
        mock_user = MagicMock()
        mock_user.is_active = True
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.role = 'COMMON_USER'
        mock_user.company = None
        mock_user_get.return_value = mock_user
        
        # Mock JWT tokens
        mock_refresh = MagicMock()
        mock_refresh.access_token = 'mock-access-token'
        mock_refresh.__str__ = lambda x: 'mock-refresh-token'
        mock_refresh_token.return_value = mock_refresh
        
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data

    @patch('core.models.CustomUser.objects.get')
    def test_login_user_inactive(self, mock_user_get):
        """Test login endpoint with inactive user"""
        # Mock inactive user
        mock_user = MagicMock()
        mock_user.is_active = False
        mock_user_get.return_value = mock_user
        
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('core.views.send_verification_email')
    @patch('core.models.CustomUser.objects.get')
    @patch('core.models.EmailVerification.objects.get')
    def test_resend_verification_email(self, mock_verification_get, mock_user_get, mock_send_email):
        """Test resending verification email endpoint"""
        # Mock user and verification
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_user.is_active = False
        mock_user_get.return_value = mock_user
        
        mock_verification = MagicMock()
        mock_verification.is_expired.return_value = False
        mock_verification_get.return_value = mock_verification
        
        # Mock email sending
        mock_send_email.return_value = None
        
        url = reverse('resend_verification')
        data = {'email': 'test@example.com'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_send_email.assert_called_once()

    @patch('core.views.send_password_reset_email')
    @patch('core.models.CustomUser.objects.get')
    @patch('core.models.EmailVerification.objects.get_or_create')
    def test_password_reset_request(self, mock_verification_get, mock_user_get, mock_send_email):
        """Test password reset request endpoint"""
        # Mock user
        mock_user = MagicMock()
        mock_user_get.return_value = mock_user
        
        # Mock verification
        mock_verification = MagicMock()
        mock_verification_get.return_value = (mock_verification, True)
        
        # Mock email sending
        mock_send_email.return_value = None
        
        url = reverse('password_reset')
        data = {'email': 'test@example.com'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_send_email.assert_called_once()

    @patch('core.models.EmailVerification.objects.get')
    def test_password_reset_confirm_success(self, mock_verification_get):
        """Test successful password reset confirmation endpoint"""
        # Mock verification
        mock_verification = MagicMock()
        mock_verification.is_expired.return_value = False
        mock_verification.user = MagicMock()
        mock_verification_get.return_value = mock_verification
        
        url = reverse('password_reset_confirm')
        data = {
            'token': 'reset-token-123',
            'new_password': 'NewSecurePass123!'
        }
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_verification.user.set_password.assert_called_once()
        mock_verification.user.save.assert_called_once()
        mock_verification.delete.assert_called_once()

    def test_user_profile_authenticated(self):
        """Test getting user profile endpoint when authenticated"""
        # Mock authenticated user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.username = 'testuser'
        mock_user.email = 'test@example.com'
        mock_user.first_name = 'Test'
        mock_user.last_name = 'User'
        mock_user.role = 'COMMON_USER'
        mock_user.company = None
        
        self.client.force_authenticate(user=mock_user)
        
        url = reverse('user_profile')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_user_profile_unauthenticated(self):
        """Test getting user profile endpoint when not authenticated"""
        url = reverse('user_profile')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('core.views.RefreshToken')
    def test_refresh_token_success(self, mock_refresh_token_class):
        """Test refresh token endpoint"""
        # Mock refresh token
        mock_refresh = MagicMock()
        mock_refresh.access_token = 'new-access-token'
        mock_refresh.__str__ = lambda x: 'new-refresh-token'
        mock_refresh_token_class.return_value = mock_refresh
        
        url = reverse('refresh_token')
        data = {'refresh_token': 'old-refresh-token'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data

    def test_refresh_token_missing(self):
        """Test refresh token endpoint without token"""
        url = reverse('refresh_token')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
