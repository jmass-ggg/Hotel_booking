from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Roles, SellerProfile
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import SellerProfile,SellerStaffProfile
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Roles.objects.filter(
            name__in=[Roles.RoleType.CUSTOMER]
        )
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data) 
        user.set_password(password)
        user.save()

        if user.role.name == Roles.RoleType.SELLER:
            SellerProfile.objects.create(user=user)

        return user

class UserMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)
    seller_profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "seller_profile_id"]

    def get_seller_profile_id(self, obj):
        seller_profile = getattr(obj, "seller_profile", None)
        return str(seller_profile.id) if seller_profile else None


class SellerStaffListSerializer(serializers.Serializer):
    username=serializers.CharField(source="user.username",read_only=True)
    email=serializers.EmailField(source="user.email",read_only=True)
    
    class Meta:
        model=SellerStaffProfile
        fields = [
            "id",
            "username",
            "email",
            "can_create",
            "can_update",
            "can_delete",
            "can_view",
        ]
    

class SellerCreateStaff(serializers.Serializer):
    
    username=serializers.CharField(write_only=True)
    email=serializers.EmailField(write_only=True)
    password=serializers.CharField(write_only=True,min_length=6)
    
    class Meta:
            model = SellerStaffProfile
            fields = [
                "id",
                "username",
                "email",
                "password",
                "can_create",
                "can_update",
                "can_delete",
                "can_view",
            ]
            read_only_fields = ["id"]
    def create(self,validated_data):
        username=validated_data.pop("username")
        email=validated_data.pop("email")
        password=validated_data.pop("password")
        
        request=self.context["request"]
        
        try:
            seller_profile=request.user.seller_profile
        except SellerProfile.DoesNotExist:
            raise serializers.ValidationError("Logged")
        seller_staff_role=Roles.objects.get(name=Roles.RoleType.SELLER_STAFF)
        user=User.objects.create_user(
            username=username
            ,email=email,
            password=password,
            role=seller_staff_role
        )
        staff_profile=SellerStaffProfile.objects.create(
            user=user,
            seller=seller_profile,
            **validated_data
        )
        return staff_profile

class SellerStaffPermissionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=SellerStaffProfile
        fields=[
            "can_create",
                "can_update",
                "can_delete",
                "can_view",
        ]
    
class AdminCreateSellerOrStaff(serializers.Serializer):
    ROLE_CHOICES = [
        Roles.RoleType.SELLER,
        Roles.RoleType.STAFF,
    ]
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role=serializers.ChoiceField(choices=ROLE_CHOICES)
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value.lower()
    @transaction.atomic
    def create(self,validated_data):
        password=validated_data.pop("password")
        role_name=validated_data.pop("role")
        role_obj=Roles.objects.get(name=role_name)
        
        user=User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
            role=role_obj,
        )
        if role_name == "SELLER":
            SellerProfile.objects.create(user=user)
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        password = attrs["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.check_password(password): 
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User is disabled.")

        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}