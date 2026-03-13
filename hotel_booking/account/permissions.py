from rest_framework.permissions import BasePermission,SAFE_METHODS
from account.models import Roles
from .models import SellerStaffProfile
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == "SELLER"  
        )

class IsSellerOwnerOfStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user,"seller_profile"):
            return False
        return obj.seller == request.user.seller_profile

class SellerStaffActionPermission(BasePermission):
    def has_permission(self, request, view):
        user=request.user
        if not user.is_authenticated:
            return False
        if user.role is None:
            return False
        if user.role.name != Roles.RoleType.SELLER_STAFF:
            return False
        try:
            staff_profile=user.seller_staff_profile
        except SellerStaffProfile.DoesNotExist:
            return False
        
        if request.method in SAFE_METHODS:
            return staff_profile.can_view
        if request.method == "POST":
            return staff_profile.can_create
        if request.method in ["PUT","PATCH"]:
            return staff_profile.can_update
        if request.method in "DELETE":
            return staff_profile.can_delete
        return False


class IsSellerWritePublicRead(BasePermission):
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True 
        return IsSeller().has_permission(request, view)
    
class IsSellerAdminOrStaffWritePublicRead(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        role_name = getattr(getattr(request.user, "role", None), "name", None)
        return role_name in ("SELLER", "ADMIN", "STAFF")
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == "CUSTOMER"
        )
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role 
            and request.user.role.name == "ADMIN"
        )


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and request.user.role 
            and request.user.role.name == "STAFF"
        )
        
class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.role
            and request.user.role.name in ("ADMIN", "STAFF")
        )