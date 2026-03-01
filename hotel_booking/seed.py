import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_booking.settings")
django.setup()

from django.contrib.auth import get_user_model
from account.models import Roles, AdminProfile

User = get_user_model()


admin_role, _ = Roles.objects.get_or_create(
    name=Roles.RoleType.ADMIN,
    defaults={"description": "System administrator"},
)

email = "admin@admin.com"
username = "admin"
password = "admin@12345"


admin_user, created = User.objects.get_or_create(
    email=email,
    defaults={"username": username},
)

if created:
    admin_user.set_password(password)

admin_user.role = admin_role
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.save()


AdminProfile.objects.get_or_create(user=admin_user)

print("Admin seeded:", admin_user.email)