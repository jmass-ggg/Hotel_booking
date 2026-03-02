from rest_framework import serializers
from .models import Property,Room,RoomPhoto,RoomType,PropertyPhoto
from django.utils import timezone
from account.models import SellerProfile


class PropertyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model=PropertyPhoto
        fields = ["id", "image", "sort_order"]
        
class RoomPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomPhoto
        fields = ["id", "image", "sort_order"]
        
class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=RoomType
        fields=["id","name","max_occupancy","base_bed_type","description"]
class PropertyPhotoUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = PropertyPhoto
        fields = ["image", "sort_order"]

class RoomPhotoUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = RoomPhoto
        fields = ["image", "sort_order"]

class PropertyPhotosBulkUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        write_only=True,
    )

class RoomPhotosBulkUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        write_only=True,
    )
class RoomSerializer(serializers.ModelSerializer):
    photos = RoomPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["id", "property", "room_type", "room_number", "floor", "status", "photos"]
        read_only_fields = ["property"]
        
class PropertySerializer(serializers.ModelSerializer):
    photos = PropertyPhotoSerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "name",
            "address",
            "city",
            "country",
            "timezone",
            "created_at",
            "photos",
            "room_types",
            "rooms",
        ]
        read_only_fields = ["id", "created_at", "photos", "room_types", "rooms"]
        
class PropertyCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Property
        fields = ["id", "name", "address", "city", "country", "timezone"]
        read_only_fields = ["id"]
    def create(self,validated_data):
        user=self.context["request"].user
        try:
            seller_profile=user.seller_profile
        except SellerProfile.DoesNotExist:
            raise serializers.ValidationError({"detail": "Only sellers can create properties."})
        return Property.objects.create(**validated_data)
    
class PropertyStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Property.Status.choices)

    def validate(self, attrs):
        prop = self.context["property"]
        new_status = attrs["status"]
        if new_status == prop.status:
            return attrs
        return attrs

    def save(self, **kwargs):
        prop = self.context["property"]
        prop.status = self.validated_data["status"]
        prop.save(update_fields=["status"])
        return prop