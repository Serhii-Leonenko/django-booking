from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from api.views import BookingViewSet, TableViewSet


app_name = "api"

router = DefaultRouter()
router.register("bookings", BookingViewSet, basename="booking")
router.register("tables", TableViewSet, basename="table")

urlpatterns = router.urls

urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
]
