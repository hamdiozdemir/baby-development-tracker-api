"""
Database models.
"""
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from datetime import date
import random
import string
import uuid


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email adress.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, role, name):
        """Create and return a superuser."""
        user = self.create_user(email, password, role=role)
        user.name = name
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """User in the System"""
    ROLES = [
        ("Tester", "Tester"),
        ("Parent", "Parent"),
        ("Staff", "Staff")
    ]
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if self.role not in ["Tester", "Parent", "Staff"]:
            raise ValueError('Please select a valid role.')
        super().save(*args, **kwargs)

        if self.role == "Tester":
            Tester.objects.create(
                user=self
            )
        elif self.role == "Parent":
            Parent.objects.create(
                user=self
            )


def slug_field_generator(size):
    """Function that returns a string for slugs."""
    slug = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=round(size/2)
            )) + "-" + ''.join(
        random.choices(
            string.ascii_lowercase + string.digits,
            k=round(size/2)))
    return slug


class Tester(models.Model):
    """Tester role model."""
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.name


class Parent(models.Model):
    """Parents role model."""
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    tester = models.ForeignKey(Tester,
                               on_delete=models.SET_NULL,
                               blank=True, null=True)

    def __str__(self):
        return self.user.name

    def add_tester(self, tester_user):
        self.tester = tester_user
        self.save()
        return self


class Child(models.Model):
    """Child object model."""
    parent = models.ForeignKey(Parent,
                               on_delete=models.CASCADE,
                               null=True, blank=True)
    tester = models.ForeignKey(Tester,
                               on_delete=models.SET_NULL,
                               null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.UUIDField(default=uuid.uuid4, auto_created=True)
    birthday = models.DateField()

    @property
    def age_in_months(self):
        """Calculate the current age in months."""
        today = date.today()
        age_in_months = round(((today - self.birthday).days) / 30)
        return age_in_months

    def add_tester(self, tester_user):
        self.tester = tester_user
        self.save()
        return self

    def add_parent(self, parent_user):
        self.parent = parent_user
        self.save()
        return self

    def add_test(self, test_id):
        """Add test and create the data in Records model."""
        test = Tests.objects.get(id=test_id)
        items = Items.objects.filter(test=test)
        for item in items:
            Records.objects.create(
                child=self,
                item=item
            )

    def __str__(self):
        return self.name


class Comments(models.Model):
    """Model for comments on a child."""
    child = models.ForeignKey(Child,
                              on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Tests(models.Model):
    """Model for all tests."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Categories(models.Model):
    """Model for Test's categories/subtests."""
    test = models.ForeignKey(Tests, related_name='categories',
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Items(models.Model):
    """Model for test items."""
    test = models.ForeignKey(Tests, related_name='items',
                             on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, related_name='items',
                                 on_delete=models.CASCADE)
    step = models.IntegerField()
    is_verbal = models.BooleanField(default=False)
    instruction = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    document = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["test", "category", "step"]

    @property
    def percents_in_months(self):
        """Query and return percents of each month of item."""
        query = Percentages.objects.filter(item=self)
        if not query.exists():
            return None
        percents = dict()
        for q in query:
            percents.update({q.month: q.percent})
        return percents

    def __str__(self):
        return self.description


class Percentages(models.Model):
    """Model for percents and months for each item."""
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    month = models.IntegerField()
    percent = models.IntegerField()


class Records(models.Model):
    """Model for each child's item records/progress."""
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    last_checkout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item} ({self.is_complete})"
