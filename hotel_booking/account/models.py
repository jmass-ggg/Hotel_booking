from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone

class Roles(models.Model):
    class RoleType(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        SELLER = "SELLER", "Seller"
        ADMIN = "ADMIN", "Admin"
        STAFF="STAFF","staff"
    name = models.CharField(max_length=20, choices=RoleType.choices, unique=True)
    description = models.CharField(max_length=255, blank=True)

def default_customer_role():
    role, _ = Roles.objects.get_or_create(name=Roles.RoleType.CUSTOMER)
    return role.id

class User(AbstractUser):
    username=models.CharField(max_length=50,unique=True)
    email=models.EmailField(max_length=50,unique=True)
    role = models.ForeignKey(
    Roles,
    on_delete=models.PROTECT,
    related_name="auth_users",
    null=True,
    blank=True,
    )
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    def __str__(self):
        return f"SellerProfile({self.user.email})"
    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")

    def __str__(self):
        return f"AdminProfile({self.user.email})"
    
