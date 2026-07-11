from django.urls import path

from tiny_api import views

urlpatterns = [
    path("tinyurl/", views.set_short_url),
    path("tinyurl/<str:short_url>/", views.get_full_url),
]
