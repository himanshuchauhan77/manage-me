from django.contrib import admin
from django.urls import include, path
from finance import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("signup/", views.signup, name="signup"),
    path("", views.app_hub, name="app_hub"),
    path("finance/", include("finance.urls")),
]
