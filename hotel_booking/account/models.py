import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Roles(models.Model):
    class RoleType(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        SELLER = "SELLER", "Seller"
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"

    name = models.CharField(max_length=20, choices=RoleType.choices, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    role = models.ForeignKey(
        Roles,
        on_delete=models.PROTECT,
        related_name="auth_users",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.username


class SellerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")

    def __str__(self):
        return f"SellerProfile({self.user.email})"


class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"AdminProfile({self.user.email})"