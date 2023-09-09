"""
Tests for models.
"""

from django.test import TestCase
from core.models import (CustomUser, Child, Comments,
                         Tests, Categories, Items, Percentages,
                         )
from datetime import (date, timedelta)


class UserReleatedModelTests(TestCase):
    """User Related Models' (CustomUser, Tester, Parent,
    Child, Comments) Tests."""

    def setUp(self):
        """Create Tester and Parent users."""
        self.tester_user = CustomUser.objects.create_user(
            email="test345@example.com",
            name="tester_user",
            password="password123",
            role="Tester"
        )

        self.parent_user = CustomUser.objects.create_user(
            email="test2@example.com",
            name="parent_user",
            password="password123",
            role="Parent"
        )

    def test_create_user_succesfuly(self):
        """Test for creating a user with email successfuly."""
        email = 'test@example.com'
        name = 'anotheruser'
        password = 'TestPass'
        role = 'Parent'
        user = CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            role=role
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.role, role)
        self.assertTrue(user.check_password(password))

    def test_create_user_role_error(self):
        """Test for return error incorrect role."""
        email = 'test@example.com'
        name = "username3"
        password = 'testpass123'
        role = "SuperAd"

        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email=email,
                name=name,
                password=password,
                role=role
                )

    def test_create_tester_user_object(self):
        email = 'test@example.com'
        name = "name2"
        password = 'testpass123'
        role = "Tester"

        CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            role=role,
        )

        tester_user_check = CustomUser.objects.filter(email=email)

        self.assertTrue(tester_user_check.exists())
        self.assertEqual(
            name,
            tester_user_check.first().name)

    def test_create_parent_user_object(self):
        email = 'test@example.com'
        name = "username2"
        password = 'testpass123'
        role = "Parent"

        CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            role=role,
        )

        parent_user_check = CustomUser.objects.filter(email=email)

        self.assertTrue(parent_user_check.exists())
        self.assertEqual(
            name,
            parent_user_check.first().name)

    def test_create_child_model_object(self):
        """Test for creating child object and calculating age in months."""
        name = "Child Name1"
        birthday = date.today() - timedelta(days=360)
        child_object = Child.objects.create(
            name=name,
            birthday=birthday
        )

        self.assertEqual(child_object.name, name)
        self.assertEqual(child_object.age_in_months, 12)

    def test_create_comment_object(self):
        """Test for creating comments."""
        child = Child.objects.create(
            name="Test Name1",
            birthday=date.today()
        )

        comment_object = Comments.objects.create(
            child=child,
            comment="NewComment"
        )

        self.assertEqual(comment_object.comment,
                         "NewComment")
        self.assertEqual(comment_object.child,
                         child)


class TestRelatedTests(TestCase):
    """Test Models Related Tests."""

    def setUp(self):
        self.test = Tests.objects.create(
            name="Denver II"
        )

    def test_create_tests_object(self):
        test = Tests.objects.create(
            name="Denver"
        )

        self.assertEqual(test.name, "Denver")

    def test_create_category(self):
        category = Categories.objects.create(
            test=self.test,
            name="Category1"
        )

        self.assertEqual(category.name, "Category1")

    def test_return_percents(self):
        """Test for returning percents of items in months."""
        category = Categories.objects.create(
            test=self.test,
            name="Motor Development"
        )
        item = Items.objects.create(
            test=self.test,
            category=category,
            step=1,
            description="Tells his/her name."
        )
        Percentages.objects.create(
            item=item,
            month=12,
            percent=25
        )
        Percentages.objects.create(
            item=item,
            month=13,
            percent=50
        )

        expected_percents = {12: 25, 13: 50}

        self.assertEqual(item.percents_in_months, expected_percents)
