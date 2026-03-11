from rest_framework import serializers
from .models import (
    Property, Room, RoomPhoto, RoomType, PropertyPhoto,
    Amenity, RoomTypeAmenity, PropertyAmenity
)
from account.models import SellerProfile


class PropertyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPhoto
        fields = ["id", "image", "sort_order"]
    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url



class RoomPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomPhoto
        fields = ["id", "image", "sort_order"]
    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url



class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = ["id", "name", "max_occupancy", "base_bed_type", "description"]


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
        fields = ["id", "property", "room_type", "room_number", "floor", "status", "price", "photos"]
        read_only_fields = ["property"]

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name", "category"]


class PropertyAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer()

    class Meta:
        model = PropertyAmenity
        fields = ["id", "amenity"]
        read_only_fields = ["id"]

    # def create(self, validated_data):
    #     amenity_data = validated_data.pop("amenity")
    #     amenity, _ = Amenity.objects.get_or_create(
    #         name=amenity_data["name"],
    #         defaults={"category": amenity_data.get("category", "")}
    #     )
    #     return PropertyAmenity.objects.create(amenity=amenity, **validated_data)

    # def update(self, instance, validated_data):
    #     amenity_data = validated_data.pop("amenity", None)

    #     if amenity_data:
    #         amenity, _ = Amenity.objects.get_or_create(
    #             name=amenity_data["name"],
    #             defaults={"category": amenity_data.get("category", "")}
    #         )
    #         instance.amenity = amenity

    #     instance.save()
    #     return instance


class RoomTypeAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer()

    class Meta:
        model = RoomTypeAmenity
        fields = ["id", "amenity"]
        read_only_fields = ["id"]

    # def create(self, validated_data):
    #     amenity_data = validated_data.pop("amenity")
    #     amenity, _ = Amenity.objects.get_or_create(
    #         name=amenity_data["name"],
    #         defaults={"category": amenity_data.get("category", "")}
    #     )
    #     return RoomTypeAmenity.objects.create(amenity=amenity, **validated_data)

    # def update(self, instance, validated_data):
    #     amenity_data = validated_data.pop("amenity", None)

    #     if amenity_data:
    #         amenity, _ = Amenity.objects.get_or_create(
    #             name=amenity_data["name"],
    #             defaults={"category": amenity_data.get("category", "")}
    #         )
    #         instance.amenity = amenity

    #     instance.save()
    #     return instance


class PropertySerializer(serializers.ModelSerializer):
    photos = PropertyPhotoSerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            "id",
            "property_name",
            "email",
            "contact_number",
            "address",
            "city",
            "country",
            "timezone",
            "status",
            "created_at",
            "photos",
            "room_types",
            "rooms",
        ]
        read_only_fields = ["id", "created_at", "photos", "room_types", "rooms"]


class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = [
            "id",
            "property_name",
            "email",
            "contact_number",
            "address",
            "city",
            "country",
            "timezone",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
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