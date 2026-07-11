from django.urls import include, path

urlpatterns = [
    path("api/", include('tiny_api.urls')),
]
