# hotel_booking/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.views import AuthViewSet
from hotels.views import PropertyViewSet, RoomTypeViewSet, RoomViewSet  # adjust import path if your app name differs
from bookings.views import BookingViewSet
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"hotels", PropertyViewSet, basename="hotels")  
router.register(r"bookings", BookingViewSet, basename="bookings")

property_room_type_list = RoomTypeViewSet.as_view({"get": "list", "post": "create"})
property_room_type_detail = RoomTypeViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

property_room_list = RoomViewSet.as_view({"get": "list", "post": "create"})
property_room_detail = RoomViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

room_photos = RoomViewSet.as_view({"get": "list_photos", "post": "upload_photo"})


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include(router.urls)),

    path("api/hotels/<int:property_pk>/room-types/", property_room_type_list, name="property-roomtype-list"),
    path("api/hotels/<int:property_pk>/room-types/<int:pk>/", property_room_type_detail, name="property-roomtype-detail"),

    path("api/hotels/<int:property_pk>/rooms/", property_room_list, name="property-room-list"),
    path("api/hotels/<int:property_pk>/rooms/<int:pk>/", property_room_detail, name="property-room-detail"),

    path("api/hotels/<int:property_pk>/rooms/<int:pk>/photos/", room_photos, name="room-photos"),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]