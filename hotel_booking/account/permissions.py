from rest_framework.permissions import BasePermission

from .models import Roles
from .accounts import get_role_name, get_actor_seller_profile

from rest_framework.permissions import IsAuthenticated
class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == Roles.RoleType.SELLER
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == Roles.RoleType.CUSTOMER
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == Roles.RoleType.ADMIN
        )


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == Roles.RoleType.STAFF
        )


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name in (
                Roles.RoleType.ADMIN,
                Roles.RoleType.STAFF,
            )
        )


class IsSellerOwnerOfStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        seller_profile = getattr(request.user, "seller_profile", None)
        return bool(seller_profile and obj.seller == seller_profile)


class SellerOrStaffScopedPermission(BasePermission):
    """
    SELLER -> full access to own resources
    SELLER_STAFF -> only allowed according to can_view/can_create/can_update/can_delete
    """

    method_flag_map = {
        "GET": "can_view",
        "HEAD": "can_view",
        "OPTIONS": "can_view",
        "POST": "can_create",
        "PUT": "can_update",
        "PATCH": "can_update",
        "DELETE": "can_delete",
    }

    def get_required_flag(self, request, view):
        action_map = getattr(view, "action_permission_map", {})
        if getattr(view, "action", None) in action_map:
            return action_map[view.action]
        return self.method_flag_map.get(request.method)

    def has_staff_flag(self, user, flag_name):
        role_name = get_role_name(user)

        if role_name == Roles.RoleType.SELLER:
            return True

        if role_name != Roles.RoleType.SELLER_STAFF:
            return False

        staff_profile = getattr(user, "seller_staff_profile", None)
        if not staff_profile:
            return False

        return getattr(staff_profile, flag_name, False)

    def get_object_seller_id(self, obj):
        if hasattr(obj, "seller_id"):
            return obj.seller_id

        if hasattr(obj, "property") and obj.property:
            return obj.property.seller_id

        if hasattr(obj, "room_type") and obj.room_type:
            return obj.room_type.property.seller_id

        if hasattr(obj, "room") and obj.room:
            return obj.room.property.seller_id

        return None

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        actor_seller = get_actor_seller_profile(user)
        if not actor_seller:
            return False

        required_flag = self.get_required_flag(request, view)
        if required_flag and not self.has_staff_flag(user, required_flag):
            return False

        if hasattr(view, "get_parent_seller_id"):
            parent_seller_id = view.get_parent_seller_id()
            if parent_seller_id and str(parent_seller_id) != str(actor_seller.id):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        actor_seller = get_actor_seller_profile(user)
        if not actor_seller:
            return False

        required_flag = self.get_required_flag(request, view)
        if required_flag and not self.has_staff_flag(user, required_flag):
            return False

        obj_seller_id = self.get_object_seller_id(obj)
        if obj_seller_id is None:
            return False

        return str(obj_seller_id) == str(actor_seller.id)
    
class IsSellerWritePublicRead(BasePermission):
    permission_classes = [IsAuthenticated, SellerOrStaffScopedPermission]