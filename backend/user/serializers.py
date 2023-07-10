"""
Serializers for the User APIs.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user objects."""

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "role"]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5},
                        'username': {'min_length': 4}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password,
        )
        if not user:
            message = _('Unable to authenticate with provided credenatials.')
            raise serializers.ValidationError(message, code='authorization')
        attrs['user'] = user
        return attrs