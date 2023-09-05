"""
URLs for the ASSESSMENT APIs.
"""

from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    path('view/', views.AssessmentsListViews.as_view(), name='list'),
    path('view/<int:pk>/', views.AssessmentDetailViews.as_view(),
         name='detail'),
]
