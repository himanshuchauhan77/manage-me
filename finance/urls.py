from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("households/", views.household_groups, name="household_groups"),
    path("households/<int:pk>/select/", views.select_household, name="select_household"),
    path("household/setup/", views.household_setup, name="household_setup"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/add/", views.transaction_create, name="transaction_create"),
    path("transactions/<int:pk>/", views.transaction_detail, name="transaction_detail"),
    path("transactions/<int:pk>/edit/", views.transaction_edit, name="transaction_edit"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
    path("categories/", views.category_list, name="category_list"), path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("goals/", views.goal_list, name="goal_list"), path("goals/<int:pk>/delete/", views.goal_delete, name="goal_delete"),
    path("analytics/", views.analytics, name="analytics"),
]
