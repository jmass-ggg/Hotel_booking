from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiExample, OpenApiParameter, OpenApiTypes
)

from account.models import SellerProfile
from account.permissions import IsSellerWritePublicRead, IsSeller,IsAdmin,IsStaff,IsAdminOrStaff

from .models import Property, RoomType, Room, PropertyPhoto, RoomPhoto,Amenity,RoomTypeAmenity,PropertyAmenity
from .serializer import (
    PropertySerializer,
    PropertyCreateSerializer,
    PropertyPhotoSerializer,
    RoomTypeSerializer,
    RoomSerializer,
    RoomPhotoSerializer,
    PropertyPhotoUploadSerializer,
    RoomPhotoUploadSerializer,
    PropertyPhotosBulkUploadSerializer,
    RoomPhotosBulkUploadSerializer,PropertyStatusUpdateSerializer,AmenitySerializer,
    PropertyAmenitySerializer,
    RoomTypeAmenitySerializer,
)



@extend_schema_view(
    list=extend_schema(summary="List properties", responses=PropertySerializer(many=True)),
    retrieve=extend_schema(summary="Retrieve a property", responses=PropertySerializer),
    create=extend_schema(
        summary="Create a property (SELLER only)",
        request=PropertyCreateSerializer,
        responses=PropertySerializer,
        examples=[
            OpenApiExample(
                "Create Property",
                value={
                    "name": "Hotel ABC",
                    "address": "Lakeside, Street 10",
                    "city": "Pokhara",
                    "country": "Nepal",
                    "timezone": "Asia/Kathmandu",
                },
            )
        ],
    ),
    update=extend_schema(summary="Update a property (SELLER only)", request=PropertyCreateSerializer, responses=PropertySerializer),
    partial_update=extend_schema(summary="Partially update a property (SELLER only)", request=PropertyCreateSerializer, responses=PropertySerializer),
    destroy=extend_schema(summary="Delete a property (SELLER only)", responses=None),
)
class PropertyViewSet(viewsets.ModelViewSet):
    
    
    permission_classes = [IsSellerWritePublicRead]

    def get_queryset(self):
        return (
            Property.objects.all()
            .select_related("seller", "seller__user")
            .prefetch_related("photos", "rooms", "room_types")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PropertyCreateSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        try:
            seller_profile = self.request.user.seller_profile
        except SellerProfile.DoesNotExist:
            raise PermissionDenied("Only sellers can create properties.")

        if hasattr(seller_profile, "property"):
            raise PermissionDenied("You already have a hotel. You cannot create more than one.")

        serializer.save(seller=seller_profile)

    def get_object(self):
        obj = super().get_object()

        role_name = getattr(getattr(self.request.user, "role", None), "name", None)
        if role_name in ("ADMIN", "STAFF"):
            return obj

        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            sp = getattr(self.request.user, "seller_profile", None)
            if not sp or obj.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        return obj

    @extend_schema(
        summary="Upload a property photo (SELLER only)",
        request={"multipart/form-data": PropertyPhotoUploadSerializer},
        responses=PropertyPhotoSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSeller],
        url_path="photos",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photo(self, request, pk=None):
        prop = self.get_object()
        s = PropertyPhotoUploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        photo = s.save(property=prop)
        return Response(PropertyPhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=PropertyStatusUpdateSerializer,
        responses=PropertyStatusUpdateSerializer,
        summary="Set property status (ADMIN/STAFF only)",
    )
    @action(
        detail=True,                       
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminOrStaff],
        url_path="set-status",
    )
    def set_status(self, request, pk=None):
        prop = self.get_object() 

        s = PropertyStatusUpdateSerializer(
            data=request.data,
            context={"property": prop},
        )
        s.is_valid(raise_exception=True)
        s.save()

        return Response(
            {"detail": "Status updated", "id": prop.id, "status": prop.status},
            status=status.HTTP_200_OK,
        )
    
    
    @extend_schema(summary="List property photos", responses=PropertyPhotoSerializer(many=True))
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None):
        prop = super().get_object()
        qs = prop.photos.all().order_by("sort_order", "id")
        return Response(PropertyPhotoSerializer(qs, many=True).data)

    @extend_schema(
        summary="Bulk upload property photos (SELLER only)",
        request={"multipart/form-data": PropertyPhotosBulkUploadSerializer},
        responses=PropertyPhotoSerializer(many=True),
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSeller],
        url_path="photos/bulk",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photos_bulk(self, request, pk=None):
        prop = self.get_object()
        s = PropertyPhotosBulkUploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        created = []
        for i, img in enumerate(s.validated_data["images"]):
            created.append(PropertyPhoto.objects.create(property=prop, image=img, sort_order=i))

        return Response(PropertyPhotoSerializer(created, many=True).data, status=status.HTTP_201_CREATED)

@extend_schema_view(
    list=extend_schema(
        summary="List room types for a property",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.INT, OpenApiParameter.PATH)],
        responses=RoomTypeSerializer(many=True),
    ),
    retrieve=extend_schema(summary="Retrieve room type", responses=RoomTypeSerializer),
    create=extend_schema(
        summary="Create room type for a property (SELLER only)",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.INT, OpenApiParameter.PATH)],
        request=RoomTypeSerializer,
        responses=RoomTypeSerializer,
    ),
    update=extend_schema(summary="Update room type (SELLER only)", request=RoomTypeSerializer, responses=RoomTypeSerializer),
    partial_update=extend_schema(summary="Partially update room type (SELLER only)", request=RoomTypeSerializer, responses=RoomTypeSerializer),
    destroy=extend_schema(summary="Delete room type (SELLER only)", responses=None),
)
class RoomTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSellerWritePublicRead]
    serializer_class = RoomTypeSerializer

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        if is_many:
            prop = Property.objects.get(id=self.kwargs["property_pk"])
            sp = request.user.seller_profile
            if prop.seller_id != sp.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not own this property.")

            serializer.save(property=prop)
        else:
            self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        return RoomType.objects.select_related("property").filter(property_id=self.kwargs["property_pk"])

    def perform_create(self, serializer):
        prop = Property.objects.get(id=self.kwargs["property_pk"])
        sp = self.request.user.seller_profile
        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")
        serializer.save(property=prop)

@extend_schema_view(
    list=extend_schema(
        summary="List rooms for a property",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.INT, OpenApiParameter.PATH)],
        responses=RoomSerializer(many=True),
    ),
    retrieve=extend_schema(summary="Retrieve room (with photos)", responses=RoomSerializer),
    create=extend_schema(
        summary="Create room for a property (SELLER only)",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.INT, OpenApiParameter.PATH)],
        request=RoomSerializer,
        responses=RoomSerializer,
        examples=[
            OpenApiExample(
                "Create Room",
                value={
  "room_type": 1,
  "room_number": "101",
  "floor": 1,
  "status": "active",
  "price": "20000"
},
            )
        ],
    ),
    update=extend_schema(summary="Update room (SELLER only)", request=RoomSerializer, responses=RoomSerializer),
    partial_update=extend_schema(summary="Partially update room (SELLER only)", request=RoomSerializer, responses=RoomSerializer),
    destroy=extend_schema(summary="Delete room (SELLER only)", responses=None),
)
class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSellerWritePublicRead]
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        is_many=isinstance(request.data,list)
        serializer=self.get_serializer(data=request.data,many=is_many)
        serializer.is_valid(raise_exception=True)
        prop=Property.objects.get(id=self.kwargs["property_pk"])
        sp=request.user.seller_profile
        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")
        if is_many:
            for item in serializer.validated_data:
                if item["room_type"].property_id != prop.id:
                    from rest_framework.exceptions import ValidationError
                    raise ValidationError(
                        {"room_type": "RoomType does not belong to this property."}
                    )
            serializer.save(property=prop)
        else:
            self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            
    def get_queryset(self):
        return (
            Room.objects.select_related("property", "room_type")
            .prefetch_related("photos")
            .filter(property_id=self.kwargs["property_pk"])
        )

    def perform_create(self, serializer):
        prop = Property.objects.get(id=self.kwargs["property_pk"])
        sp = self.request.user.seller_profile
        if prop.seller_id != sp.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this property.")

        room_type = serializer.validated_data["room_type"]
        if room_type.property_id != prop.id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"room_type": "RoomType does not belong to this property."})

        serializer.save(property=prop)


    @extend_schema(
        summary="Upload a room photo (SELLER only)",
        request={"multipart/form-data": RoomPhotoUploadSerializer},
        responses=RoomPhotoSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSeller],
        url_path="photos",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photo(self, request, pk=None, property_pk=None):
        room = self.get_object()
        sp = request.user.seller_profile
        if room.property.seller_id != sp.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this room/property.")

        s = RoomPhotoUploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        photo = s.save(room=room)
        return Response(RoomPhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="List room photos", responses=RoomPhotoSerializer(many=True))
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None, property_pk=None):
        room = self.get_object()
        qs = room.photos.all().order_by("sort_order", "id")
        return Response(RoomPhotoSerializer(qs, many=True).data)


    @extend_schema(
    summary="Upload a property photo (SELLER only)",
    request=PropertyPhotoUploadSerializer,
    responses=PropertyPhotoSerializer,
)
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSeller],
        url_path="photos/bulk",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photos_bulk(self, request, pk=None, property_pk=None):
        room = self.get_object()
        sp = request.user.seller_profile
        if room.property.seller_id != sp.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this room/property.")

        s = RoomPhotosBulkUploadSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        created = []
        for i, img in enumerate(s.validated_data["images"]):
            created.append(RoomPhoto.objects.create(room=room, image=img, sort_order=i))

        return Response(RoomPhotoSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
@extend_schema_view(
    list=extend_schema(summary="List all amenities", responses=AmenitySerializer(many=True)),
    retrieve=extend_schema(summary="Retrieve amenity", responses=AmenitySerializer),
    create=extend_schema(summary="Create amenity", request=AmenitySerializer, responses=AmenitySerializer),
    update=extend_schema(summary="Update amenity", request=AmenitySerializer, responses=AmenitySerializer),
    partial_update=extend_schema(summary="Partial update amenity", request=AmenitySerializer, responses=AmenitySerializer),
    destroy=extend_schema(summary="Delete amenity", responses=None),
)
class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all().order_by("name")
    serializer_class = AmenitySerializer
    permission_classes = [IsSellerWritePublicRead]
    
class PropertyAmenityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSellerWritePublicRead]
    serializer_class = PropertyAmenitySerializer

    def get_property(self):
        prop = get_object_or_404(Property, id=self.kwargs["property_pk"])
        return prop

    def get_queryset(self):
        prop = self.get_property()
        return (
            PropertyAmenity.objects
            .select_related("property", "amenity")
            .filter(property=prop)
            .order_by("id")
        )

    def perform_create(self, serializer):
        prop = self.get_property()
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or prop.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data["amenity"]

        if PropertyAmenity.objects.filter(property=prop, amenity=amenity).exists():
            raise ValidationError({"amenity": "This amenity is already added to this property."})

        serializer.save(property=prop)

    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or obj.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data.get("amenity", obj.amenity)

        if PropertyAmenity.objects.filter(
            property=obj.property,
            amenity=amenity
        ).exclude(id=obj.id).exists():
            raise ValidationError({"amenity": "This amenity is already added to this property."})

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        role_name = getattr(getattr(user, "role", None), "name", None)

        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or instance.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        instance.delete()


class RoomTypeAmenityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSellerWritePublicRead]
    serializer_class = RoomTypeAmenitySerializer

    def get_room_type(self):
        room_type = get_object_or_404(
            RoomType.objects.select_related("property"),
            id=self.kwargs["room_type_pk"],
            property_id=self.kwargs["property_pk"],
        )
        return room_type

    def get_queryset(self):
        room_type = self.get_room_type()
        return (
            RoomTypeAmenity.objects
            .select_related("room_type", "room_type__property", "amenity")
            .filter(room_type=room_type)
            .order_by("id")
        )

    def perform_create(self, serializer):
        room_type = self.get_room_type()
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or room_type.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data["amenity"]

        if RoomTypeAmenity.objects.filter(room_type=room_type, amenity=amenity).exists():
            raise ValidationError({"amenity": "This amenity is already added to this room type."})

        serializer.save(room_type=room_type)

    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or obj.room_type.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data.get("amenity", obj.amenity)

        if RoomTypeAmenity.objects.filter(
            room_type=obj.room_type,
            amenity=amenity
        ).exclude(id=obj.id).exists():
            raise ValidationError({"amenity": "This amenity is already added to this room type."})

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        role_name = getattr(getattr(user, "role", None), "name", None)

        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or instance.room_type.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        instance.delete()