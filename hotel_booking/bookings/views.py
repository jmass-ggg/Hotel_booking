from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from account.permissions import IsCustomer
from .models import Booking
from .serializer import BookingCreateSerializer, BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCustomer]
    queryset = Booking.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.role and user.role.name == "CUSTOMER":
            return (
                Booking.objects.select_related("property", "room_type", "room", "customer")
                .prefetch_related("guests")
                .filter(customer=user)
                .order_by("-created_at")
            )

        sp = getattr(user, "seller_profile", None)
        if sp:
            return (
                Booking.objects.select_related("property", "room_type", "room", "customer")
                .prefetch_related("guests")
                .filter(property__seller=sp)
                .order_by("-created_at")
            )

        return Booking.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.role and user.role.name == "CUSTOMER"):
            raise PermissionDenied("Only customers can create bookings.")
        serializer.save()