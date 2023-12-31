"""
Serializers for the User APIs.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers
from core.models import Child
from assessment.serializers import AssesmentsListSerializer


class ChildSerializer(serializers.ModelSerializer):
    """Serializer for Child obj."""

    class Meta:
        model = Child
        fields = ["id", "name", "birthday", "age_in_months"]


class ChildDetailSerializer(ChildSerializer):
    """Child detail serializer with including tests etc."""

    tests = AssesmentsListSerializer(many=True, required=False)

    class Meta:
        model = Child
        fields = ChildSerializer.Meta.fields + ["tests"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user objects."""

    child = ChildSerializer(many=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ["email", "name", "password", "role", "child"]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5},
                        'username': {'min_length': 4}}
        read_only_fields = ["child"]

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        if validated_data.get('child'):
            validated_data.pop('child')
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        if validated_data.get('child'):
            payload = validated_data.pop('child')
            for child_data in payload:
                child_obj = Child.objects.create(**child_data)
                self.instance.child.add(child_obj)

        if validated_data.get('role'):
            validated_data.pop('role')
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password,
        )
        if not user:
            message = _('Unable to authenticate with provided credenatials.')
            raise serializers.ValidationError(message, code='authorization')
        attrs['user'] = user
        return attrs
