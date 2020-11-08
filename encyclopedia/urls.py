from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("user", views.user, name="user"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("wiki/<str:title>/log", views.logger, name="log"),
    path("search", views.search, name="search"),
    path("random", views.rand, name="random"),
    path("create", views.create, name="create"),
    path("edit/<str:title>", views.edit, name="edit"),
]
