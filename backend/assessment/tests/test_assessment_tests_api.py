"""
Tests retrieving for assesment tools.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Tests,
    Categories,
    Items,)
from assessment.serializers import (
    AssesmentsListSerializer,
    AssessmentDetailSerializer)

ASSESSMENT_TEST_LIST_URL = reverse('assessment:list')


def detail_url(test_id):
    """Create and return a test's/assessment's detail url."""
    return reverse('assessment:detail', args=[test_id])


def create_test_details(test1, test2):
    """Create test, category and items for testings."""
    category1 = Categories.objects.create(test=test1, name="Cat1")
    category2 = Categories.objects.create(test=test1, name="Cat2")
    category3 = Categories.objects.create(test=test2, name="Cat3")
    Items.objects.bulk_create([
        Items(
            test=test1,
            category=category1,
            step=1,
            instruction="testing item1"
        ),
        Items(
            test=test1,
            category=category1,
            step=2,
            instruction="testing item2"
        ),
        Items(
            test=test1,
            category=category2,
            step=3,
            instruction="testing item3"
        ),
        Items(
            test=test2,
            category=category3,
            step=1,
            instruction="testing item4"
        )]
    )


class AssessmentRetrivingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.test1 = Tests.objects.create(name='Denver II')
        self.test2 = Tests.objects.create(name='TEAMS 3')

        self.user = get_user_model().objects.create_user(
            name='newuser',
            email='test123@example.com',
            password='testpassword',
            role='Parent'
        )

    def test_retrieve_assessments_list(self):
        """Test for retriving tests list."""
        response = self.client.get(ASSESSMENT_TEST_LIST_URL)

        tests = Tests.objects.all()
        serializer = AssesmentsListSerializer(tests, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(tests.count(), 2)

    def test_retrieve_assessment_details(self):
        """Test for retrieving a tests' categories and items."""

        create_test_details(self.test1, self.test2)

        self.client.force_authenticate(user=self.user)
        url = detail_url(self.test1.id)
        response = self.client.get(url)
        serializer = AssessmentDetailSerializer(self.test1)

        self.assertEqual(len(response.data['categories']), 2)
        self.assertEqual(len(response.data['categories'][0]['items']), 2)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_assessment_detail_not_authenticated(self):
        """Test for retrieving tests/tools detail for not auths."""

        create_test_details(self.test1, self.test2)

        url = detail_url(self.test1.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assessment_edit_not_allowed(self):
        """Test for assessment details POST, PATCH, DELETE not allowed
        for regular users."""

        create_test_details(self.test1, self.test2)

        url = detail_url(self.test1.id)
        payload = {'name': 'New Name'}
        # self.client.force_authenticate(user=self.user)
        response_patch = self.client.patch(url, payload)
        response_post = self.client.post(url, payload)
        response_delete = self.client.delete(url)

        self.assertIn(response_patch.status_code,
                      [401, 403, 405])
        self.assertIn(response_post.status_code,
                      [401, 403, 405])
        self.assertIn(response_delete.status_code,
                      [401, 403, 405])

    def test_assessment_edit_allowed_for_staff_users(self):
        """Test for assesment details POST, PATCH, DELETE allowed
        for staff users."""

        create_test_details(self.test1, self.test2)
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        url = detail_url(self.test1.id)
        payload = {'name': 'New Test Name'}
        response = self.client.patch(url, payload)
        # PATCHING
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test1.refresh_from_db()
        self.assertEqual(self.test1.name, payload['name'])
        # DELETING
        url2 = detail_url(self.test2.id)
        response2 = self.client.delete(url2)
        query = Tests.objects.filter(name='TEAMS 3').exists()
        self.assertEqual(response2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(query)
