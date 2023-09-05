"""
Views for Asssessment APIs.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import AssesmentsListSerializer, AssessmentDetailSerializer
from core.models import Tests


class AssessmentsListViews(generics.ListAPIView):
    """Views for retriving tests' lists."""
    queryset = Tests.objects.all()
    serializer_class = AssesmentsListSerializer

    def get_queryset(self):
        return super().get_queryset()


class AssessmentDetailViews(generics.RetrieveAPIView):
    """View for retriving tests' details."""

    queryset = Tests.objects.all()
    serializer_class = AssessmentDetailSerializer

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(queryset, pk=pk)
        return obj
