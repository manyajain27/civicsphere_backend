from django.urls import re_path, path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *
from .serializers import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="CivicSphere API",
        default_version="v1",
        description="API documentation for CivicSphere",
        terms_of_service="https://www.yourwebsite.com/terms/",
        contact=openapi.Contact(email="support@yourwebsite.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    
    # Swagger Documentation
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-ui"),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),

    # Authentication APIs
    # Authentication APIs
    path('auth/register/', RegisterView.as_view(), name='register'),  # Returns user + tokens
    path('auth/login/', LoginView.as_view(), name='login'),  # Custom login view with tokens
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),  # Default refresh


    # Job APIs (Restricted to Workers or Customers)
    path('jobs/', CustomerJobListView.as_view(), name='customer-job-list'), 
    path('jobs/open/', JobListView.as_view(), name='job-list'), 
    path('jobs/create/', JobCreateView.as_view(), name='job-create'), 
    path('jobs/<int:pk>/update/', JobUpdateView.as_view(), name='job-update'), 
    path('jobs/<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'), 
    path('jobs/<int:pk>/accept/', AcceptJobView.as_view(), name='job-accept'), 
    path('jobs/assigned/', WorkerAssignedJobsView.as_view(), name='worker-jobs'), 
    path('jobs/<int:pk>/offers/', JobOfferView.as_view(), name='job-offer'),



    # Worker List APIs (Only Customers can see Workers)
    path('workers/', WorkerListView.as_view(), name='worker-list'),

    # Reviews & Ratings
    path('reviews/customer/', CustomerReviewCreateView.as_view(), name='customer-review'),  # Only Workers can review Customers
    path('reviews/worker/', WorkerReviewCreateView.as_view(), name='worker-review'),  # Only Customers can review Workers

    #User Profile
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),

]
