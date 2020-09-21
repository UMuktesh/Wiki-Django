from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.wiki, name="wiki"),
    path("search", views.search, name="search"),
    path("random", views.rand, name="random"),
    path("create", views.create, name="create"),
    path("edit/<str:title>", views.edit, name="edit"),
]
