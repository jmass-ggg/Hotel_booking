from django.contrib import admin
from account.models import SellerProfile 
from django.conf import settings
from django.db import models
from django.utils import timezone
from account.models import SellerProfile
class Property(models.Model):
    seller_id=models.ForeignKey(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name="properties"
    )
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64, default="UTC")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}"
    
class RoomType(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="room_types")

    name = models.CharField(max_length=100) 
    max_occupancy = models.PositiveSmallIntegerField(default=2)
    base_bed_type = models.CharField(max_length=50, blank=True) 
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.property.name} - {self.name}"
    
class Room(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        OUT_OF_ORDER = "out_of_order", "Out of order"

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name="rooms")

    room_number = models.CharField(max_length=20)
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
           
            models.UniqueConstraint(fields=["property", "room_number"], name="uniq_room_per_property")
        ]
        indexes = [
            models.Index(fields=["property", "room_type"]),
            models.Index(fields=["property", "room_number"]),
        ]

    def __str__(self):
        return f"{self.property.name} - Room {self.room_number}"
    
class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="properties/")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Photo for {self.property.name} #{self.id}"
    
class RoomPhoto(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="photos")
    image=models.ImageField(upload_to="room_type/")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]