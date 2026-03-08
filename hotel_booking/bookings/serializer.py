from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from .models import Booking, BookingGuest


class BookingGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingGuest
        fields = ["id", "full_name", "email", "phone"]


class BookingSerializer(serializers.ModelSerializer):
    guests = BookingGuestSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer",
            "property",
            "room_type",
            "room",
            "check_in",
            "check_out",
            "adults",
            "children",
            "status",
            "total_amount",
            "created_at",
            "updated_at",
            "guests",
        ]
        read_only_fields = fields


class BookingCreateSerializer(serializers.ModelSerializer):
    guests = BookingGuestSerializer(many=True, write_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "property",
            "room_type",
            "room",
            "check_in",
            "check_out",
            "adults",
            "children",
            "guests",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        if not (user.role and user.role.name == "CUSTOMER"):
            raise serializers.ValidationError("Only customers can create bookings.")

        check_in = attrs["check_in"]
        check_out = attrs["check_out"]
        prop = attrs["property"]
        room_type = attrs["room_type"]
        room = attrs.get("room")

        if check_in >= check_out:
            raise serializers.ValidationError({"check_out": "check_out must be after check_in."})

        if not getattr(prop, "is_hotel", True):
            raise serializers.ValidationError({"property": "Only hotels can be booked."})

        if room_type.property_id != prop.id:
            raise serializers.ValidationError({"room_type": "RoomType does not belong to this property."})
        if getattr(prop, "status", None) != "approved":
            raise serializers.ValidationError({"property": "This property is not accepted yet, so it cannot be booked."})
        if room:
            if room.property_id != prop.id:
                raise serializers.ValidationError({"room": "Room does not belong to this property."})
            if room.room_type_id != room_type.id:
                raise serializers.ValidationError({"room": "Room does not match the selected room_type."})

            conflict = Booking.objects.filter(
                room=room,
                status__in=[
                    Booking.Status.PENDING,
                    Booking.Status.CONFIRMED,
                    Booking.Status.CHECKED_IN,
                ],
            ).filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
            ).exists()

            if conflict:
                raise serializers.ValidationError({"room": "This room is not available for the selected dates."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        guests_data = validated_data.pop("guests", [])
        user = self.context["request"].user

        booking = Booking.objects.create(customer=user, **validated_data)

        BookingGuest.objects.bulk_create(
            [BookingGuest(booking=booking, **g) for g in guests_data]
        )
        return booking