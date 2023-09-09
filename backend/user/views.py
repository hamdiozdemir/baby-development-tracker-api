"""
Views for user API.
"""

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from core.models import Child

from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ChildDetailSerializer)


class CreateUserView(generics.CreateAPIView):
    """Create a new user."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Retrieve and Update the auth user."""
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return the auth user object."""
        return self.request.user


class ChildRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Manage child object for authorized users."""
    queryset = Child.objects.all()
    serializer_class = ChildDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        return get_object_or_404(queryset, pk=pk)

    def get(self, request, *args, **kwargs):
        # If child object in users' child field.
        if request.user.child.filter(id=self.kwargs.get('pk')).exists():
            return super().get(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        # If child object in users' child field.
        if request.user.child.filter(id=self.kwargs.get('pk')).exists():
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, *args, **kwargs):
        # If child object in users' child field.
        if request.user.child.filter(id=self.kwargs.get('pk')).exists():
            return super().delete(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
