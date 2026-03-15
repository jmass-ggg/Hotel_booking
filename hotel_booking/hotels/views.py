from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

from account.accounts import get_actor_seller_profile
from account.permissions import IsAdminOrStaff, SellerOrStaffScopedPermission

from .models import (
    Amenity,
    Property,
    PropertyAmenity,
    PropertyPhoto,
    Room,
    RoomPhoto,
    RoomType,
    RoomTypeAmenity,
)
from .serializer import (
    AmenitySerializer,
    PropertyAmenitySerializer,
    PropertyCreateSerializer,
    PropertyPhotoSerializer,
    PropertyPhotoUploadSerializer,
    PropertyPhotosBulkUploadSerializer,
    PropertySerializer,
    PropertyStatusUpdateSerializer,
    RoomPhotoSerializer,
    RoomPhotoUploadSerializer,
    RoomPhotosBulkUploadSerializer,
    RoomSerializer,
    RoomTypeAmenitySerializer,
    RoomTypeSerializer,
)


class SellerScopedNestedMixin:
    permission_classes = [IsAuthenticated, SellerOrStaffScopedPermission]

    def get_parent_property(self):
        return get_object_or_404(
            Property.objects.only("id", "seller_id"),
            id=self.kwargs["property_pk"],
        )

    def get_parent_seller_id(self):
        return self.get_parent_property().seller_id


@extend_schema_view(
    list=extend_schema(
        summary="List properties",
        responses=PropertySerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve a property",
        responses=PropertySerializer,
    ),
    create=extend_schema(
        summary="Create a property",
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
        summary="Update a property",
        request=PropertyCreateSerializer,
        responses=PropertySerializer,
    ),
    partial_update=extend_schema(
        summary="Partial update a property",
        request=PropertyCreateSerializer,
        responses=PropertySerializer,
    ),
    destroy=extend_schema(
        summary="Delete a property",
        responses=None,
    ),
)
class PropertyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, SellerOrStaffScopedPermission]

    action_permission_map = {
        "retrieve": "can_view",
        "my": "can_view",
        "create": "can_create",
        "update": "can_update",
        "partial_update": "can_update",
        "destroy": "can_delete",
        "upload_photo": "can_create",
        "list_photos": "can_view",
        "upload_photos_bulk": "can_create",
    }

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]

        if self.action == "set_status":
            return [IsAuthenticated(), IsAdminOrStaff()]

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        return (
            Property.objects.select_related("seller", "seller__user")
            .prefetch_related(
                "photos",
                "rooms",
                "room_types",
                "property_amenities__amenity",
                "room_types__room_type_amenities__amenity",
            )
            .all()
        )

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return PropertyCreateSerializer
        return PropertySerializer

    def perform_create(self, serializer):
        seller_profile = get_actor_seller_profile(self.request.user)
        if not seller_profile:
            raise PermissionDenied("Only seller account users can create properties.")

        if Property.objects.filter(seller=seller_profile).exists():
            raise PermissionDenied("You already have a hotel. You cannot create more than one.")

        serializer.save(seller=seller_profile)

    @extend_schema(
        summary="Get current seller hotel",
        responses=PropertySerializer,
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated, SellerOrStaffScopedPermission],
        url_path="my",
    )
    def my(self, request):
        seller_profile = get_actor_seller_profile(request.user)
        if not seller_profile:
            return Response(None, status=status.HTTP_200_OK)

        prop = (
            Property.objects.select_related("seller", "seller__user")
            .prefetch_related(
                "photos",
                "rooms",
                "room_types",
                "property_amenities__amenity",
                "room_types__room_type_amenities__amenity",
            )
            .filter(seller=seller_profile)
            .first()
        )

        if not prop:
            return Response(None, status=status.HTTP_200_OK)

        return Response(PropertySerializer(prop, context={"request": request}).data)

    @extend_schema(
        summary="Upload a property photo",
        request={"multipart/form-data": PropertyPhotoUploadSerializer},
        responses=PropertyPhotoSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, SellerOrStaffScopedPermission],
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
        summary="List property photos",
        responses=PropertyPhotoSerializer(many=True),
    )
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None):
        prop = self.get_object()
        photos = prop.photos.all().order_by("sort_order", "id")
        return Response(
            PropertyPhotoSerializer(
                photos,
                many=True,
                context={"request": request},
            ).data
        )

    @extend_schema(
        summary="Bulk upload property photos",
        request={"multipart/form-data": PropertyPhotosBulkUploadSerializer},
        responses=PropertyPhotoSerializer(many=True),
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, SellerOrStaffScopedPermission],
        url_path="photos/bulk",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photos_bulk(self, request, pk=None):
        prop = self.get_object()
        serializer = PropertyPhotosBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created = []
        with transaction.atomic():
            for index, image in enumerate(serializer.validated_data["images"]):
                created.append(
                    PropertyPhoto.objects.create(
                        property=prop,
                        image=image,
                        sort_order=index,
                    )
                )

        return Response(
            PropertyPhotoSerializer(
                created,
                many=True,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Set property status",
        request=PropertyStatusUpdateSerializer,
        responses=PropertyStatusUpdateSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsAdminOrStaff],
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

        prop.refresh_from_db(fields=["status"])

        return Response(
            {
                "detail": "Status updated",
                "id": prop.id,
                "status": prop.status,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List room types for a property",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        responses=RoomTypeSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve room type",
        responses=RoomTypeSerializer,
    ),
    create=extend_schema(
        summary="Create room type for a property",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        request=RoomTypeSerializer,
        responses=RoomTypeSerializer,
    ),
    update=extend_schema(
        summary="Update room type",
        request=RoomTypeSerializer,
        responses=RoomTypeSerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update room type",
        request=RoomTypeSerializer,
        responses=RoomTypeSerializer,
    ),
    destroy=extend_schema(
        summary="Delete room type",
        responses=None,
    ),
)
class RoomTypeViewSet(SellerScopedNestedMixin, viewsets.ModelViewSet):
    serializer_class = RoomTypeSerializer

    action_permission_map = {
        "list": "can_view",
        "retrieve": "can_view",
        "create": "can_create",
        "update": "can_update",
        "partial_update": "can_update",
        "destroy": "can_delete",
    }

    def get_queryset(self):
        return (
            RoomType.objects.select_related("property")
            .filter(property_id=self.kwargs["property_pk"])
            .order_by("id")
        )

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        prop = self.get_parent_property()
        serializer.save(property=prop)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(
        summary="List rooms for a property",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        responses=RoomSerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve room",
        responses=RoomSerializer,
    ),
    create=extend_schema(
        summary="Create room for a property",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        request=RoomSerializer,
        responses=RoomSerializer,
    ),
    update=extend_schema(
        summary="Update room",
        request=RoomSerializer,
        responses=RoomSerializer,
    ),
    partial_update=extend_schema(
        summary="Partially update room",
        request=RoomSerializer,
        responses=RoomSerializer,
    ),
    destroy=extend_schema(
        summary="Delete room",
        responses=None,
    ),
)
class RoomViewSet(SellerScopedNestedMixin, viewsets.ModelViewSet):
    serializer_class = RoomSerializer

    action_permission_map = {
        "list": "can_view",
        "retrieve": "can_view",
        "create": "can_create",
        "update": "can_update",
        "partial_update": "can_update",
        "destroy": "can_delete",
        "upload_photo": "can_create",
        "list_photos": "can_view",
        "upload_photos_bulk": "can_create",
    }

    def get_queryset(self):
        return (
            Room.objects.select_related("property", "room_type")
            .prefetch_related("photos")
            .filter(property_id=self.kwargs["property_pk"])
            .order_by("id")
        )

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        prop = self.get_parent_property()
        validated_items = serializer.validated_data if is_many else [serializer.validated_data]

        for item in validated_items:
            room_type = item.get("room_type")
            if room_type.property_id != prop.id:
                raise ValidationError(
                    {"room_type": "RoomType does not belong to this property."}
                )

        serializer.save(property=prop)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Upload a room photo",
        request={"multipart/form-data": RoomPhotoUploadSerializer},
        responses=RoomPhotoSerializer,
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, SellerOrStaffScopedPermission],
        url_path="photos",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photo(self, request, pk=None, property_pk=None):
        room = self.get_object()
        serializer = RoomPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        photo = serializer.save(room=room)
        return Response(
            RoomPhotoSerializer(photo, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="List room photos",
        responses=RoomPhotoSerializer(many=True),
    )
    @upload_photo.mapping.get
    def list_photos(self, request, pk=None, property_pk=None):
        room = self.get_object()
        photos = room.photos.all().order_by("sort_order", "id")
        return Response(
            RoomPhotoSerializer(
                photos,
                many=True,
                context={"request": request},
            ).data
        )

    @extend_schema(
        summary="Upload room photos in bulk",
        request={"multipart/form-data": RoomPhotosBulkUploadSerializer},
        responses=RoomPhotoSerializer(many=True),
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, SellerOrStaffScopedPermission],
        url_path="photos/bulk",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_photos_bulk(self, request, pk=None, property_pk=None):
        room = self.get_object()
        serializer = RoomPhotosBulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created = []
        with transaction.atomic():
            for index, image in enumerate(serializer.validated_data["images"]):
                created.append(
                    RoomPhoto.objects.create(
                        room=room,
                        image=image,
                        sort_order=index,
                    )
                )

        return Response(
            RoomPhotoSerializer(
                created,
                many=True,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(
        summary="List all amenities",
        responses=AmenitySerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve amenity",
        responses=AmenitySerializer,
    ),
    create=extend_schema(
        summary="Create amenity",
        request=AmenitySerializer,
        responses=AmenitySerializer,
    ),
    update=extend_schema(
        summary="Update amenity",
        request=AmenitySerializer,
        responses=AmenitySerializer,
    ),
    partial_update=extend_schema(
        summary="Partial update amenity",
        request=AmenitySerializer,
        responses=AmenitySerializer,
    ),
    destroy=extend_schema(
        summary="Delete amenity",
        responses=None,
    ),
)
class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all().order_by("name")
    serializer_class = AmenitySerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrStaff()]


@extend_schema_view(
    list=extend_schema(
        summary="List property amenities",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        responses=PropertyAmenitySerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve property amenity",
        responses=PropertyAmenitySerializer,
    ),
    create=extend_schema(
        summary="Create property amenity",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH)
        ],
        request=PropertyAmenitySerializer,
        responses=PropertyAmenitySerializer,
    ),
    update=extend_schema(
        summary="Update property amenity",
        request=PropertyAmenitySerializer,
        responses=PropertyAmenitySerializer,
    ),
    partial_update=extend_schema(
        summary="Partial update property amenity",
        request=PropertyAmenitySerializer,
        responses=PropertyAmenitySerializer,
    ),
    destroy=extend_schema(
        summary="Delete property amenity",
        responses=None,
    ),
)
class PropertyAmenityViewSet(SellerScopedNestedMixin, viewsets.ModelViewSet):
    serializer_class = PropertyAmenitySerializer

    action_permission_map = {
        "list": "can_view",
        "retrieve": "can_view",
        "create": "can_create",
        "update": "can_update",
        "partial_update": "can_update",
        "destroy": "can_delete",
    }

    def get_queryset(self):
        prop = self.get_parent_property()
        return (
            PropertyAmenity.objects.select_related("property", "amenity")
            .filter(property=prop)
            .order_by("id")
        )

    def perform_create(self, serializer):
        prop = self.get_parent_property()
        amenity_data = serializer.validated_data["amenity"]

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if PropertyAmenity.objects.filter(property=prop, amenity=amenity).exists():
            raise ValidationError(
                {"amenity": "This amenity is already added to this property."}
            )

        serializer.save(property=prop, amenity=amenity)

    def perform_update(self, serializer):
        obj = self.get_object()
        amenity_data = serializer.validated_data.get("amenity")

        if not amenity_data:
            serializer.save()
            return

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if (
            PropertyAmenity.objects.filter(property=obj.property, amenity=amenity)
            .exclude(id=obj.id)
            .exists()
        ):
            raise ValidationError(
                {"amenity": "This amenity is already added to this property."}
            )

        serializer.save(amenity=amenity)


@extend_schema_view(
    list=extend_schema(
        summary="List room type amenities",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH),
            OpenApiParameter("room_type_pk", OpenApiTypes.UUID, OpenApiParameter.PATH),
        ],
        responses=RoomTypeAmenitySerializer(many=True),
    ),
    retrieve=extend_schema(
        summary="Retrieve room type amenity",
        responses=RoomTypeAmenitySerializer,
    ),
    create=extend_schema(
        summary="Create room type amenity",
        parameters=[
            OpenApiParameter("property_pk", OpenApiTypes.UUID, OpenApiParameter.PATH),
            OpenApiParameter("room_type_pk", OpenApiTypes.UUID, OpenApiParameter.PATH),
        ],
        request=RoomTypeAmenitySerializer,
        responses=RoomTypeAmenitySerializer,
    ),
    update=extend_schema(
        summary="Update room type amenity",
        request=RoomTypeAmenitySerializer,
        responses=RoomTypeAmenitySerializer,
    ),
    partial_update=extend_schema(
        summary="Partial update room type amenity",
        request=RoomTypeAmenitySerializer,
        responses=RoomTypeAmenitySerializer,
    ),
    destroy=extend_schema(
        summary="Delete room type amenity",
        responses=None,
    ),
)
class RoomTypeAmenityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, SellerOrStaffScopedPermission]
    serializer_class = RoomTypeAmenitySerializer

    action_permission_map = {
        "list": "can_view",
        "retrieve": "can_view",
        "create": "can_create",
        "update": "can_update",
        "partial_update": "can_update",
        "destroy": "can_delete",
    }

    def get_room_type(self):
        return get_object_or_404(
            RoomType.objects.select_related("property").only(
                "id",
                "property_id",
                "property__seller_id",
            ),
            id=self.kwargs["room_type_pk"],
            property_id=self.kwargs["property_pk"],
        )

    def get_parent_seller_id(self):
        return self.get_room_type().property.seller_id

    def get_queryset(self):
        room_type = self.get_room_type()
        return (
            RoomTypeAmenity.objects.select_related(
                "room_type",
                "room_type__property",
                "amenity",
            )
            .filter(room_type=room_type)
            .order_by("id")
        )

    def perform_create(self, serializer):
        room_type = self.get_room_type()
        amenity_data = serializer.validated_data["amenity"]

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if RoomTypeAmenity.objects.filter(room_type=room_type, amenity=amenity).exists():
            raise ValidationError(
                {"amenity": "This amenity is already added to this room type."}
            )

        serializer.save(room_type=room_type, amenity=amenity)

    def perform_update(self, serializer):
        obj = self.get_object()
        amenity_data = serializer.validated_data.get("amenity")

        if not amenity_data:
            serializer.save()
            return

        amenity, _ = Amenity.objects.get_or_create(
            name=amenity_data["name"],
            defaults={"category": amenity_data.get("category", "")},
        )

        if (
            RoomTypeAmenity.objects.filter(room_type=obj.room_type, amenity=amenity)
            .exclude(id=obj.id)
            .exists()
        ):
            raise ValidationError(
                {"amenity": "This amenity is already added to this room type."}
            )

        serializer.save(amenity=amenity)