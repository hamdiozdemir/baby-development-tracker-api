"""
URLs for the USER APIs.
"""

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('profile/', views.ManageUserView.as_view(), name='profile'),
    path('child/<int:pk>/', views.ChildRetrieveUpdateDestroyView.as_view(),
         name='child-detail'),
]
