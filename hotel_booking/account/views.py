from rest_framework import generics,permissions,status,viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializer import RegisterSerializer,LoginSerializer
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema

class AuthViewSet(viewsets.ViewSet):
    @extend_schema(request=RegisterSerializer,responses=RegisterSerializer)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self,request):
        serializers=RegisterSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            user=serializers.save()
            return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name if user.role else None, 
            },
            status=status.HTTP_201_CREATED,
        )
            
            
    @extend_schema(request=LoginSerializer,responses=LoginSerializer)
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self,request):
        serializers=LoginSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        return Response(serializers.validated_data, status=status.HTTP_200_OK)
            