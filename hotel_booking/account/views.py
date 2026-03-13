from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .models import SellerProfile,SellerStaffProfile
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    AdminCreateSellerOrStaff,SellerCreateStaff,
    UserMeSerializer,SellerCreateStaff,SellerStaffPermissionUpdateSerializer,SellerStaffListSerializer
)
from .throttles import RegisterRateThrottle, LoginRateThrottle
from .permissions import IsAdmin,IsSeller,IsSellerOwnerOfStaff
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, viewsets, serializers
class AuthViewSet(viewsets.ViewSet):
    @extend_schema(request=RegisterSerializer, responses=RegisterSerializer)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        throttle_classes=[RegisterRateThrottle],
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name if user.role else None,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(request=LoginSerializer, responses=LoginSerializer)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        throttle_classes=[LoginRateThrottle],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @extend_schema(responses=UserMeSerializer)
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=AdminCreateSellerOrStaff, responses=AdminCreateSellerOrStaff)
    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def create_seller_or_staff(self, request):
        serializer = AdminCreateSellerOrStaff(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name if user.role else None,
            },
            status=status.HTTP_201_CREATED,
        )
        
class SellerViewSet(viewsets.ModelViewSet):
    permission_classes=[IsSeller,IsSellerOwnerOfStaff]
    lookup_field="id"
    lookup_url_kwarg="staff_id"
    
    def get_queryset(self):
        return SellerStaffProfile.objects.filter(
            seller=self.request.user.seller_profile
        ).select_related(
            "user","seller","seller__user"
        )
    def get_serializer_class(self):
        if self.action == "create":
            return SellerCreateStaff
        elif self.action == "permissions":
            return SellerStaffPermissionUpdateSerializer
        return SellerStaffListSerializer
    @extend_schema(
        responses=SellerStaffListSerializer(many=True),
        summary="List seller staff",
        description="List all staff members created under the logged-in seller.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @extend_schema(
        request=SellerCreateStaff,
        responses=SellerStaffListSerializer,
        summary="Create seller staff",
        description="Create a new seller staff user under the logged-in seller.",
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_profile = serializer.save()

        return Response(
            {
                "id": str(staff_profile.id),
                "username": staff_profile.user.username,
                "email": staff_profile.user.email,
                "role": staff_profile.user.role.name if staff_profile.user.role else None,
                "can_create": staff_profile.can_create,
                "can_update": staff_profile.can_update,
                "can_delete": staff_profile.can_delete,
                "can_view": staff_profile.can_view,
            },
            status=status.HTTP_201_CREATED,
        )
    @extend_schema(
        responses=SellerStaffListSerializer,
        summary="Retrieve seller staff",
        description="Retrieve one seller staff by UUID.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    @extend_schema(
        responses={
            204:None
        },summary="Delete seller staff",
        description="Delete a seller staff user and its linked user account.",
    )
    def destroy(self, request, *args, **kwargs):
        instance=self.get_object()
        user=instance.user
        instance.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    @extend_schema(
        request=SellerStaffPermissionUpdateSerializer,
        responses=inline_serializer(
            name="SellerStaffPermissionUpdateResponse",
            fields={
                "message": serializers.CharField(),
                "staff_id": serializers.UUIDField(),
                "permissions": SellerStaffPermissionUpdateSerializer(),
            },
        ),
        summary="Update seller staff permissions",
        description="Directly update only permission flags for a seller staff user.",
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="permissions",
        permission_classes=[IsAuthenticated, IsSeller, IsSellerOwnerOfStaff],
    )
    def permissions(self, request, *args, **kwargs):
        instance=self.get_object()
        serializer=self.get_serializer(
            instance,data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": "Seller staff permissions updated successfully.",
                "staff_id": str(instance.id),
                "permissions": serializer.data,
            },
            status=status.HTTP_200_OK,
        )