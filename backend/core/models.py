"""
Database models.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


class CustomUser(AbstractUser):
    """Our own custom user with extra fields."""
    ROLES = [
        ("Tester", "Tester"),
        ("Parent", "Parent"),
        ("Staff", "Staff")
    ]
    role = models.CharField(max_length=50, choices=ROLES)

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


class Tester(models.Model):
    """Tester role model."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Parent(models.Model):
    """Parents role model."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tester = models.ForeignKey(Tester,
                               on_delete=models.SET_NULL,
                               blank=True, null=True)

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
    birthday = models.DateField()

    @property
    def age_in_months(self):
        """Calculate the current age in months."""
        today = date.today()
        age_in_months = (today.year - self.birthday.year) * \
            12 + (today.month - self.birthday.month)
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
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Instructions(models.Model):
    """Model for instruction for some items."""
    name = models.CharField(max_length=255)
    document = models.CharField(max_length=255, null=True, blank=True)


class Items(models.Model):
    """Model for test items."""
    test = models.ForeignKey(Tests, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    step = models.IntegerField()
    is_verbal = models.BooleanField(default=False)
    instruction = models.ForeignKey(Instructions,
                                    on_delete=models.SET_NULL,
                                    null=True, blank=True)
    description = models.CharField(max_length=255)

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
