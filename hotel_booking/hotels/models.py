import uuid
from django.db import models
from account.models import SellerProfile


class Property(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "DRAFT"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"
        REJECTED = "rejected", "Rejected"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.OneToOneField(
        SellerProfile,
        on_delete=models.CASCADE,
        related_name="property",
    )
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64, default="UTC")
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


class RoomType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name="rooms")
    room_number = models.CharField(max_length=20)
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="properties/")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"Photo for {self.property.name} #{self.id}"


class RoomPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="room_type/")
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]


class Amenity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PropertyAmenity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="property_amenities")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name="property_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["property", "amenity"], name="uniq_property_amenity")
        ]

    def __str__(self):
        return f"{self.property.name} - {self.amenity.name}"


class RoomTypeAmenity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="room_type_amenities")
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name="room_type_links")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["room_type", "amenity"], name="uniq_room_type_amenity")
        ]

    def __str__(self):
        return f"{self.room_type} - {self.amenity.name}"