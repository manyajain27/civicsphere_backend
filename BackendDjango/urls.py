from django.urls import path
from base.views import (
    CustomTokenObtainPairView, 
    CustomTokenRefreshView
)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("", include("base.urls"))
]
