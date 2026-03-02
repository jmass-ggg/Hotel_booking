from rest_framework import viewsets ,status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiExample, OpenApiParameter, OpenApiTypes
)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from .models import Booking
from account.permissions import IsCustomer
from .serializer import  (
    BookingCreateSerializer,BookingSerializers,BookingGuestSerializers
)
@extend_schema_view(
    list=extend_schema(
        summary="List bookings",
        description=(
            "CUSTOMER: returns only their own bookings.\n"
            "SELLER: returns bookings for properties owned by that seller.\n"
            "Other roles: empty list."
        ),
        responses=BookingSerializers(many=True),
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Optional filter by status (pending/confirmed/cancelled/checked_in/checked_out).",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a booking",
        description="Access rules are the same as list: CUSTOMER sees own; SELLER sees bookings for their properties.",
        responses=BookingSerializers,
    ),
    create=extend_schema(
        summary="Create a booking (CUSTOMER only)",
        description=(
            "Only users with role CUSTOMER can create a booking.\n"
            "Creates booking + nested guests in one request.\n"
            "If room is provided, it checks date overlap to prevent double-booking that room."
        ),
        request=BookingCreateSerializer,
        responses=BookingSerializers,
        examples=[
            OpenApiExample(
                name="Create booking (room_type only, room not assigned yet)",
                value={
                    "property": 10,
                    "room_type": 7,
                    "room": None,
                    "check_in": "2026-03-10",
                    "check_out": "2026-03-12",
                    "adults": 2,
                    "children": 0,
                    "guests": [
                        {"full_name": "Ram Shrestha", "email": "ram@gmail.com", "phone": "98xxxxxxx"}
                    ],
                },
            ),
            OpenApiExample(
                name="Create booking (exact room selected)",
                value={
                    "property": 10,
                    "room_type": 7,
                    "room": 25,
                    "check_in": "2026-03-10",
                    "check_out": "2026-03-12",
                    "adults": 1,
                    "children": 0,
                    "guests": [
                        {"full_name": "Sita Shrestha", "email": "sita@gmail.com", "phone": "98xxxxxxx"}
                    ],
                },
            ),
        ],
    ),
    
)
class BookingViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset = Booking.objects.all()
    
    def get_queryset(self):
        user=self.request.user
        if user.role and user.role.name == "CUSTOMER":
            return (
                Booking.objects.select_related("property", "room_type", "room", "customer")
                .prefetch_related("guests")
                .filter(customer=user).order_by("-create_at")
            )
        sp=getattr(user,"seller_profile",None)
        if sp:
            return (
                Booking.objects.select_related("property", "room_type", "room", "customer")
                .prefetch_related("guests")
                .filter(property_seller=sp).order_by("-created_at")
                            )
    def get_serializer_class(self):
        if self.action in ("create"):
            return BookingCreateSerializer
        return BookingSerializers
    def perform_create(self, serializer):
        user=self.request.user
        if not(user.role and user.role.name == "CUSTOMER"):
            raise PermissionDenied("only customer can create bookings")
        serializer.save()
        