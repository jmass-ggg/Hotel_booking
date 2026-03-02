from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from hotels.models import Property,RoomType,Room

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"
    customer=models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    property=models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    room_type=models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    room=models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
    )
    check_in=models.DateField()
    check_out=models.DateField()
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.check_in>=self.check_out:
            raise ValidationError({"check_out": "check_out must be after check_in."})
        if self.room_type_id and self.property_id:
            if self.room_type.property_id != self.property_id:
                raise ValidationError({"room_type": "RoomType does not belong to this property."})
        if self.room_id:
            if self.room.property_id != self.property_id:
                raise ValidationError({"room": "Room does not belong to this property."})
            if self.room.room_type_id != self.room_type_id:
                raise ValidationError({"room": "Room does not match the selected room_type."})

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking({self.id}) {self.customer_id} {self.property_id} {self.check_in}→{self.check_out}"


class BookingGuest(models.Model):
    booking=models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="guests"
        
    )
    full_name=models.CharField(max_length=50,null=False)
    email=models.CharField(null=False)
    phone=models.CharField(max_length=30,blank=True)
    def __str__(self):
        return f"Guest({self.full_name}) for Booking({self.booking_id})"