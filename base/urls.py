from django.urls import path, include
from rest_framework.routers import *
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
