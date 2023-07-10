"""
Tests for the User APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Tests for public features of the user APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user(self):
        """Test creating a new user succesfuly."""
        payload = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass',
            'role': 'Parent'
        }

        response = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_username_exists_error(self):
        """Test for username does not exists."""
        payload = {
            'email': 'test2222@example.com',
            'username': 'newuser',
            'password': 'qwewer2123',
            'role': 'Parent'
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_email_exists_error(self):
        """Test for username does not exists."""
        payload = {
            'email': 'test@example.com',
            'username': 'newuser22',
            'password': 'qwewer2123',
            'role': 'Parent'
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test for password lenght."""
        payload = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'pwd',
            'role': 'Tester'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        check_user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(check_user_exists)

    def test_username_too_short_error(self):
        """Test for password lenght."""
        payload = {
            'email': 'test@example.com',
            'username': 'te',
            'password': 'pwdqwerty1',
            'role': 'Tester'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        check_user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(check_user_exists)

    def test_no_role_error(self):
        """Test for not have a valid role."""
        payload = {
            'email': 'test@example.com',
            'username': 'te',
            'password': 'pwdqwerty1',
            'role': ''
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        check_user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(check_user_exists)

    def test_create_token_for_user(self):
        """Test creates token for a valid user credentials."""
        user_details = {
            'email': 'test@example.com',
            'username': 'testuser1',
            'password': 'pwdqwerty1',
            'role': 'Tester'
        }
        create_user(**user_details)
        payload = {
            'username': user_details['username'],
            'password': user_details['password']
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error for invalid credenatials."""
        create_user(
            email='test@example.com',
            username='testuser',
            password='Validpass',
            role='Tester'
        )

        payload = {
            'username': 'testuser',
            'password': 'Invalidpass'
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password_error(self):
        """Test for blank password return error."""
        payload = {
            'username': 'testuser',
            'password': ''
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile_unauthorized(self):
        """Test for failing unauthorized profile retrive."""
        response = self.client.get(PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
