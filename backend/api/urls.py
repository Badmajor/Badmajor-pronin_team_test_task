from django.urls import include, path
from rest_framework import routers

from .views import CollectViewSet

router = routers.DefaultRouter()
router.register(r"collects", CollectViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
