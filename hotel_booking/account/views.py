from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    AdminCreateSellerOrStaff,
    UserMeSerializer,
)
from .throttles import RegisterRateThrottle, LoginRateThrottle
from .permissions import IsAdmin


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