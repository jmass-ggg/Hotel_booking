from rest_framework.permissions import BasePermission,SAFE_METHODS
from account.models import Roles

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == "SELLER"  
        )

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