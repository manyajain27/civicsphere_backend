from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
    # Authentication APIs
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Job APIs (Restricted to Workers or Customers)
    path('jobs/', JobListView.as_view(), name='job-list'),  # Open for all (Modify if needed)
    path('jobs/create/', JobCreateView.as_view(), name='job-create'),  # Only Customers
    path('jobs/update/<int:pk>/', JobUpdateView.as_view(), name='job-update'),  # Only Customers

    # Worker APIs (Only Customers can see Workers)
    path('workers/', WorkerListView.as_view(), name='worker-list'),

    # Reviews & Ratings
    path('reviews/customer/', CustomerReviewCreateView.as_view(), name='customer-review'),  # Only Workers can review Customers
    path('reviews/worker/', WorkerReviewCreateView.as_view(), name='worker-review'),  # Only Customers can review Workers
]
