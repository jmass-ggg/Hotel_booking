from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiExample, OpenApiParameter, OpenApiTypes
)
from django.shortcuts import get_object_or_404

from account.models import SellerProfile
from account.permissions import (
    IsSellerWritePublicRead,
    IsSeller,
    IsAdminOrStaff,
)

from .models import (
    Property, RoomType, Room, PropertyPhoto, RoomPhoto,
    Amenity, RoomTypeAmenity, PropertyAmenity
)
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
    RoomPhotosBulkUploadSerializer,
    PropertyStatusUpdateSerializer,
    AmenitySerializer,
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
                    "property_name": "Hotel ABC",
                    "email": "hotelabc@example.com",
                    "contact_number": "+9779800000000",
                    "address": "Lakeside, Street 10",
                    "city": "Pokhara",
                    "country": "Nepal",
                    "timezone": "Asia/Kathmandu",
                },
            )
        ],
    ),
    update=extend_schema(
        summary="Update a property (SELLER only)",
        request=PropertyCreateSerializer,
        responses=PropertySerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update a property (SELLER only)",
        request=PropertyCreateSerializer,
        responses=PropertySerializer,
    ),
    destroy=extend_schema(summary="Delete a property (SELLER only)", responses=None),
)
class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSellerWritePublicRead]

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]

        if self.action in ["by_seller", "by_name"]:
            return [IsAuthenticated(), IsSeller()]

        if self.action == "set_status":
            return [IsAuthenticated(), IsAdminOrStaff()]

        return [permission() for permission in self.permission_classes]
    
    def get_queryset(self):
        queryset = (
            Property.objects.all()
            .select_related("seller", "seller__user")
            .prefetch_related(
                "photos",
                "rooms",
                "room_types",
                "property_amenities__amenity",
                "room_types__room_type_amenities__amenity",
            )
        )
        return queryset
        return queryset
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

        user = self.request.user
        role_name = getattr(getattr(user, "role", None), "name", None)

        # hotel by id -> only admin/staff/seller
        if self.action == "retrieve":
            if not user.is_authenticated:
                raise PermissionDenied("Authentication required.")

            if role_name not in ("ADMIN", "STAFF", "SELLER"):
                raise PermissionDenied("Only admin, staff, or seller can view hotel by id.")

        # write operations -> seller owner or admin/staff
        if self.request.method not in ("GET", "HEAD", "OPTIONS"):
            if role_name in ("ADMIN", "STAFF"):
                return obj

            sp = getattr(user, "seller_profile", None)
            if not sp or obj.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        return obj
    @extend_schema(
        summary="Get current seller's hotel",
        responses=PropertySerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, IsSeller],
        url_path="my",
    )
    def my(self, request):
        sp = getattr(request.user, "seller_profile", None)
        if not sp:
            return Response(None, status=status.HTTP_200_OK)

        prop = (
            Property.objects.select_related("seller", "seller__user")
            .prefetch_related("photos", "rooms", "room_types")
            .filter(seller=sp)
            .first()
        )

        if not prop:
            return Response(None, status=status.HTTP_200_OK)

        return Response(
            PropertySerializer(prop, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )
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
        serializer = PropertyPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(property=prop)
        return Response(
            PropertyPhotoSerializer(photo, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
    @extend_schema(
        request=PropertyStatusUpdateSerializer,
        responses=PropertyStatusUpdateSerializer,
        summary="Set property status (ADMIN/STAFF only)",
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[ IsAdminOrStaff],
        url_path="set-status",
    )
    def set_status(self, request, pk=None):
        prop = self.get_object()

        serializer = PropertyStatusUpdateSerializer(
            data=request.data,
            context={"property": prop},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Status updated", "id": prop.id, "status": prop.status},
            status=status.HTTP_200_OK,
        )

    @extend_schema(summary="List property photos", responses=PropertyPhotoSerializer(many=True))
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None):
        prop = super().get_object()
        qs = prop.photos.all().order_by("sort_order", "id")
        return Response(
            PropertyPhotoSerializer(qs, many=True, context={"request": request}).data
        )
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
        serializer = PropertyPhotosBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created = []
        for i, img in enumerate(serializer.validated_data["images"]):
            created.append(
                PropertyPhoto.objects.create(
                    property=prop,
                    image=img,
                    sort_order=i,
                )
            )

        return Response(
            PropertyPhotoSerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    list=extend_schema(
        summary="List room types for a property",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        responses=RoomTypeSerializer(many=True),
    ),
    retrieve=extend_schema(summary="Retrieve room type", responses=RoomTypeSerializer),
    create=extend_schema(
        summary="Create room type for a property (SELLER only)",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)],
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

        prop = get_object_or_404(Property, id=self.kwargs["property_pk"])
        sp = request.user.seller_profile

        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")

        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return RoomType.objects.select_related("property").filter(property_id=self.kwargs["property_pk"])

    def perform_create(self, serializer):
        prop = get_object_or_404(Property, id=self.kwargs["property_pk"])
        sp = self.request.user.seller_profile

        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")

        serializer.save(property=prop)


@extend_schema_view(
    list=extend_schema(
        summary="List rooms for a property",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        responses=RoomSerializer(many=True),
    ),
    retrieve=extend_schema(summary="Retrieve room (with photos)", responses=RoomSerializer),
    create=extend_schema(
        summary="Create room for a property (SELLER only)",
        parameters=[OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        request=RoomSerializer,
        responses=RoomSerializer,
        examples=[
            OpenApiExample(
                "Create Room",
                value={
                    "room_type": "room-type-uuid",
                    "room_number": "101",
                    "floor": 1,
                    "status": "active",
                    "price": "20000",
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
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        prop = get_object_or_404(Property, id=self.kwargs["property_pk"])
        sp = request.user.seller_profile

        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")

        validated_items = serializer.validated_data if is_many else [serializer.validated_data]
        for item in validated_items:
            if item["room_type"].property_id != prop.id:
                raise ValidationError({"room_type": "RoomType does not belong to this property."})

        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return (
            Room.objects.select_related("property", "room_type")
            .prefetch_related("photos")
            .filter(property_id=self.kwargs["property_pk"])
        )

    def perform_create(self, serializer):
        prop = get_object_or_404(Property, id=self.kwargs["property_pk"])
        sp = self.request.user.seller_profile

        if prop.seller_id != sp.id:
            raise PermissionDenied("You do not own this property.")

        room_type = serializer.validated_data["room_type"]
        if room_type.property_id != prop.id:
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
            raise PermissionDenied("You do not own this room/property.")

        serializer = RoomPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = serializer.save(room=room)
        return Response(RoomPhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="List room photos", responses=RoomPhotoSerializer(many=True))
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None, property_pk=None):
        room = self.get_object()
        qs = room.photos.all().order_by("sort_order", "id")
        return Response(
            RoomPhotoSerializer(qs, many=True, context={"request": request}).data
        )

    @extend_schema(
        summary="Upload room photos in bulk (SELLER only)",
        request={"multipart/form-data": RoomPhotosBulkUploadSerializer},
        responses=RoomPhotoSerializer(many=True),
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
            raise PermissionDenied("You do not own this room/property.")

        serializer = RoomPhotosBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created = []
        for i, img in enumerate(serializer.validated_data["images"]):
            created.append(
                RoomPhoto.objects.create(
                    room=room,
                    image=img,
                    sort_order=i,
                )
            )

        return Response(
            RoomPhotoSerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

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
        return get_object_or_404(Property, id=self.kwargs["property_pk"])

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

        amenity_data = serializer.validated_data["amenity"]

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if PropertyAmenity.objects.filter(property=prop, amenity=amenity).exists():
            raise ValidationError({"amenity": "This amenity is already added to this property."})

        serializer.save(property=prop, amenity=amenity)

    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or obj.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data.get("amenity", obj.amenity)
        if PropertyAmenity.objects.filter(property=obj.property, amenity=amenity).exclude(id=obj.id).exists():
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
        return get_object_or_404(
            RoomType.objects.select_related("property"),
            id=self.kwargs["room_type_pk"],
            property_id=self.kwargs["property_pk"],
        )

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

        amenity_data = serializer.validated_data["amenity"]

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if RoomTypeAmenity.objects.filter(room_type=room_type, amenity=amenity).exists():
            raise ValidationError({"amenity": "This amenity is already added to this room type."})

        serializer.save(room_type=room_type, amenity=amenity)
    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user

        role_name = getattr(getattr(user, "role", None), "name", None)
        if role_name not in ("ADMIN", "STAFF"):
            sp = getattr(user, "seller_profile", None)
            if not sp or obj.room_type.property.seller_id != sp.id:
                raise PermissionDenied("You do not own this property.")

        amenity = serializer.validated_data.get("amenity", obj.amenity)
        if RoomTypeAmenity.objects.filter(room_type=obj.room_type, amenity=amenity).exclude(id=obj.id).exists():
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