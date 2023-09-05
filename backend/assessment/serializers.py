"""
Serializers for the Assessment APIs.
"""

from rest_framework import serializers
from core.models import (
    Tests,
    Categories,
    Items,
    )


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for items."""

    class Meta:
        model = Items
        fields = ['step', 'instruction', 'description']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    items = ItemSerializer(many=True)

    class Meta:
        model = Categories
        fields = ['id', 'name', 'items']


class AssesmentsListSerializer(serializers.ModelSerializer):
    """Serializer for listing assessment tools/tests."""

    class Meta:
        model = Tests
        fields = "__all__"


class AssessmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for assessment tools/tests details."""

    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = Tests
        fields = ['id', 'name', 'categories']
