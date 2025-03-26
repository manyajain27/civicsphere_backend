from django.urls import path
from base.views import (
    CustomTokenObtainPairView, 
    CustomTokenRefreshView
)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("base.urls"))
]
