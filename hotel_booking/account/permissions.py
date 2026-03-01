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

class IsCustomer(BasePermission):
    def has_permission(self,request,view):
        return bool(
            request.user and
            request.user.is_authenticated
            and getattr(request.user.role) == "CUSTOMER"
        )
    