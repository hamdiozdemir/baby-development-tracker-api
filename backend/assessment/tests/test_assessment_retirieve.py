"""
Tests retrieving for assesment tools.
"""

from django.test import TestCase
from django.urls import reverse

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


class AssessmentRetrivingTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.test1 = Tests.objects.create(name='Denver II')
        self.test2 = Tests.objects.create(name='TEAMS 3')

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

        category1 = Categories.objects.create(test=self.test1, name="Cat1")
        category2 = Categories.objects.create(test=self.test1, name="Cat2")

        category3 = Categories.objects.create(test=self.test2, name="Cat3")

        Items.objects.bulk_create([
            Items(
                test=self.test1,
                category=category1,
                step=1,
                instruction="testing item1"
            ),
            Items(
                test=self.test1,
                category=category1,
                step=2,
                instruction="testing item2"
            ),
            Items(
                test=self.test1,
                category=category2,
                step=3,
                instruction="testing item3"
            ),
            Items(
                test=self.test2,
                category=category3,
                step=1,
                instruction="testing item4"
            )]
        )

        url = detail_url(self.test1.id)
        response = self.client.get(url)
        serializer = AssessmentDetailSerializer(self.test1)
        self.assertEqual(len(response.data['categories']), 2)
        self.assertEqual(len(response.data['categories'][0]['items']), 2)
        self.assertEqual(response.data, serializer.data)

    def test_assessment_other_request_not_allowed(self):
        """Test for assessment details POST, PATCH, DELETE not allowed."""

        category1 = Categories.objects.create(test=self.test1, name="Cat1")
        category2 = Categories.objects.create(test=self.test1, name="Cat2")

        category3 = Categories.objects.create(test=self.test2, name="Cat3")

        Items.objects.bulk_create([
            Items(
                test=self.test1,
                category=category1,
                step=1,
                instruction="testing item1"
            ),
            Items(
                test=self.test1,
                category=category1,
                step=2,
                instruction="testing item2"
            ),
            Items(
                test=self.test1,
                category=category2,
                step=3,
                instruction="testing item3"
            ),
            Items(
                test=self.test2,
                category=category3,
                step=1,
                instruction="testing item4"
            )]
        )

        url = detail_url(self.test1.id)
        payload = {'name': 'New Name'}
        response_patch = self.client.patch(url, payload)
        response_post = self.client.post(url, payload)
        response_delete = self.client.delete(url)

        self.assertEqual(response_patch.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_post.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response_delete.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
