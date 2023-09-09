"""
Tests for the User APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Child
from user.serializers import UserSerializer, ChildDetailSerializer
import datetime

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def child_detail_url(child_id):
    """Create and return url for child obj."""
    return reverse('user:child-detail', args=[child_id])


class PublicUserAPITests(TestCase):
    """Tests for public features of the user APIs."""

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user(self):
        """Test creating a new user succesfuly."""
        payload = {
            'name': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass',
            'role': 'Parent'
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_name_exists_error(self):
        """Test for name does not exists."""
        payload = {
            'email': 'test2222@example.com',
            'name': 'newuser',
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
            'name': 'newuser22',
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
            'name': 'testuser',
            'password': 'pwd',
            'role': 'Tester'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        check_user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(check_user_exists)

    def test_no_role_error(self):
        """Test for not have a valid role."""
        payload = {
            'email': 'test@example.com',
            'name': 'te',
            'password': 'pwdqwerty1',
            'role': ''
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        check_user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(check_user_exists)

    def test_create_token_for_user(self):
        """Test creates token for a valid user credentials."""
        user_details = {
            'email': 'test@example.com',
            'name': 'testuser1',
            'password': 'pwdqwerty1',
            'role': 'Tester'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test return error for invalid credenatials."""
        create_user(
            email='test@example.com',
            name='testuser',
            password='Validpass',
            role='Tester'
        )

        payload = {
            'email': 'test@example.com',
            'password': 'Invalidpass'
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password_error(self):
        """Test for blank password return error."""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile_unauthorized(self):
        """Test for failing unauthorized profile retrive."""
        response = self.client.get(PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API for rquests that reqiure auth."""

    def setUp(self):
        payload = {
            'name': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass',
            'role': 'Parent'
        }
        self.user = create_user(**payload)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        response = self.client.get(PROFILE_URL)
        serializer = UserSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_profile_not_allowed(self):
        """Test POST request is not allowed for profile endpoint."""
        response = self.client.post(PROFILE_URL, {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """Test for updating user profile for the auth users."""
        payload = {'password': "NewPassword"}

        response = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_role_not_changed(self):
        """Test for update user profile only with password and email field."""
        payload = {
            'name': "NewUserName",
            'password': 'NewPassword134',
            'email': 'newemail@example.com',
            'role': 'Tester'
        }

        response = self.client.patch(PROFILE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.email, payload['email'])
        self.assertEqual(self.user.name, payload['name'])
        self.assertNotEqual(self.user.role, payload['role'])


class ChildObjectsTests(TestCase):
    """Tests for child objects."""

    def setUp(self):
        payload = {
            'name': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass',
            'role': 'Parent'
        }
        self.user = create_user(**payload)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_child_profile_not_authorized(self):
        """Test for retrieving a child's profile not authorized."""

        child_obj = Child.objects.create(
            name="Mike",
            birthday=datetime.date(2010, 9, 25)
        )
        url = child_detail_url(child_id=child_obj.id)
        response_get = self.client.get(url)

        self.assertEqual(response_get.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_patch_child_profile_not_authorized(self):
        """Test for updating a child's profile not authorized."""

        child_obj = Child.objects.create(
            name="Mike",
            birthday=datetime.date(2010, 9, 25)
        )
        url = child_detail_url(child_id=child_obj.id)
        payload = {
            'name': "Micheal"
        }
        response_patch = self.client.patch(url, payload)

        self.assertEqual(response_patch.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(child_obj.name,
                            payload['name'])

    def test_delete_child_profile_not_authorized(self):
        """Test for deleting a child's profile not authorized."""

        child_obj = Child.objects.create(
            name="Mike",
            birthday=datetime.date(2010, 9, 25)
        )
        url = child_detail_url(child_id=child_obj.id)
        response_delete = self.client.delete(url)

        self.assertEqual(response_delete.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Child.objects.filter(name='Mike').exists())

    def test_get_child_obj_successful(self):
        """Test for retrieving child object successfully."""

        child_obj = Child.objects.create(
            name="Maike",
            birthday=datetime.date(2021, 2, 15)
        )
        self.user.child.add(child_obj)
        self.user.refresh_from_db()
        url = child_detail_url(child_id=child_obj.id)
        response = self.client.get(url)
        serializer = ChildDetailSerializer(child_obj)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_add_child_to_user_successful(self):
        """Test for adding a child to user successfuly."""
        payload = {'child': [
            {'name': "New Child",
            'birthday': datetime.date(2020, 8, 20)}
        ]}
        response = self.client.patch(PROFILE_URL, payload, format='json')
        self.user.refresh_from_db()

        serializer = UserSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data['child'][0]['name'],
                         payload['child'][0]['name'])
