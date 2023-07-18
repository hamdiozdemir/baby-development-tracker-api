"""
Tests for models.
"""

from django.test import TestCase
from core.models import (CustomUser, Tester, Parent, Child, Comments,
                         Tests, Categories, Items, Percentages,
                         Records)
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
        self.tester = Tester.objects.get(user=self.tester_user)
        self.parent = Parent.objects.get(user=self.parent_user)

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

        user = CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            role=role,
        )

        tester_user_check = Tester.objects.filter(user=user)

        self.assertTrue(tester_user_check.exists())
        self.assertEqual(
            user.name,
            tester_user_check.first().user.name)

    def test_create_parent_user_object(self):
        email = 'test@example.com'
        name = "username2"
        password = 'testpass123'
        role = "Parent"

        user = CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            role=role,
        )

        parent_user_check = Parent.objects.filter(user=user)

        self.assertTrue(parent_user_check.exists())
        self.assertEqual(
            user.name,
            parent_user_check.first().user.name)

    def test_create_child_model_object(self):
        """Test for creating child object and calculating age in months."""
        name = "Child Name1"
        birthday = date.today() - timedelta(days=360)
        parent = Parent.objects.get(user=self.parent_user)
        child_object = Child.objects.create(
            parent=parent,
            name=name,
            birthday=birthday
        )

        self.assertEqual(child_object.name, name)
        self.assertEqual(child_object.age_in_months, 12)

    def test_add_tester_to_parent_object(self):
        """Test for adding tester to Parent object."""
        parent_user = Parent.objects.get(user=self.parent_user)
        tester_user = Tester.objects.get(user=self.tester_user)
        parent_user.add_tester(tester_user)

        self.assertEqual(tester_user.id, parent_user.tester.id)

    def test_add_tester_to_child_object(self):
        """Test for adding tester to Parent object."""
        child_object = Child.objects.create(
            parent=self.parent,
            name="Test Name1",
            birthday=date.today()
        )
        child_object.add_tester(self.tester)

        self.assertEqual(self.tester.id,
                         child_object.tester.id)

    def test_add_parent_to_child_object(self):
        """Test for adding parent to Parent object."""
        child_object = Child.objects.create(
            tester=self.tester,
            name="Test Name2",
            birthday=date.today()
        )
        child_object.add_parent(self.parent)

        self.assertEqual(self.parent.id,
                         child_object.parent.id)

    def test_create_comment_object(self):
        """Test for creating comments."""
        child = Child.objects.create(
            parent=self.parent,
            tester=self.tester,
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

    def test_add_test_to_child_object(self):
        """Test for adding test to a child successfully."""
        child = Child.objects.create(
            name="Test Name",
            birthday=date.today() - timedelta(days=1500)
        )
        category1 = Categories.objects.create(
            test=self.test,
            name="Category1"
        )
        category2 = Categories.objects.create(
            test=self.test,
            name="Category2"
        )
        items = [
            Items(
                test=self.test,
                category=category1,
                step=1,
                description="test item 1"
            ),
            Items(
                test=self.test,
                category=category1,
                step=2,
                description="test item 2"
            ),
            Items(
                test=self.test,
                category=category2,
                step=1,
                description="test item 3"
            )
        ]
        Items.objects.bulk_create(items)

        child.add_test(self.test.id)

        records_query = Records.objects.filter(child=child)

        self.assertEqual(len(records_query), 3)
