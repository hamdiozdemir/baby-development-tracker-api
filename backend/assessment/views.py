"""
Views for Asssessment APIs.
"""

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import AssesmentsListSerializer, AssessmentDetailSerializer
from .permissions import IsStaffOrReadOnly
from core.models import Tests


class AssessmentsListViews(generics.ListAPIView):
    """Views for retriving tests' lists."""
    queryset = Tests.objects.all()
    serializer_class = AssesmentsListSerializer

    def get_queryset(self):
        return super().get_queryset()


class AssessmentDetailViews(generics.RetrieveUpdateDestroyAPIView):
    """View for retriving tests' details."""

    queryset = Tests.objects.all()
    serializer_class = AssessmentDetailSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(queryset, pk=pk)
        return obj
