from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password-change/",
        views.password_change,
        name="password_change",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("theme/toggle/", views.toggle_theme, name="toggle_theme"),
    path("theme/accent/<str:color>/", views.set_accent, name="set_accent"),
    # Admin
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("admin-panel/users/create/", views.admin_user_create, name="admin_user_create"),
    path("budgets/", views.budget_list, name="budget_list"),
    path("budgets/create/", views.budget_create, name="budget_create"),
    path("budgets/<int:pk>/edit/", views.budget_edit, name="budget_edit"),
    path("budgets/<int:pk>/assign/", views.budget_assign, name="budget_assign"),
    path("budgets/<int:pk>/members/", views.budget_members, name="budget_members"),
    path(
        "budgets/<int:pk>/members/<int:user_pk>/remove/",
        views.budget_member_remove,
        name="budget_member_remove",
    ),
    # Budget user area
    path(
        "budgets/<int:pk>/dashboard/",
        views.budget_dashboard,
        name="budget_dashboard",
    ),
    path(
        "budgets/<int:budget_pk>/categories/",
        views.category_list,
        name="category_list",
    ),
    path(
        "budgets/<int:budget_pk>/categories/create/",
        views.category_create,
        name="category_create",
    ),
    path(
        "budgets/<int:budget_pk>/categories/<int:pk>/edit/",
        views.category_edit,
        name="category_edit",
    ),
    path(
        "budgets/<int:budget_pk>/categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    path(
        "budgets/<int:budget_pk>/expenses/",
        views.expense_list,
        name="expense_list",
    ),
    path(
        "budgets/<int:budget_pk>/expenses/create/",
        views.expense_create,
        name="expense_create",
    ),
    path(
        "budgets/<int:budget_pk>/expenses/<int:pk>/edit/",
        views.expense_edit,
        name="expense_edit",
    ),
    path(
        "budgets/<int:budget_pk>/expenses/<int:pk>/delete/",
        views.expense_delete,
        name="expense_delete",
    ),
]
