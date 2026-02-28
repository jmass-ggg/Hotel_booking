from rest_framework import serializers
from .models import Property,Room,RoomPhoto,RoomType,PropertyPhoto
from django.utils import timezone
from account.models import SellerProfile


# class PropertyRegister(serializers.Serializer):
#     class Meta:
#         model=Property
#         fields=[
#             "id","name","address","city","country",
#         ]
#     def create(self,validated_data):
#         user = self.context["request"].user

#         try:
#             seller_profile = user.seller_profile  
#         except SellerProfile.DoesNotExist:
#             raise serializers.ValidationError({"seller_profile": "Unauthorized."})

#         return Property.objects.create(seller=seller_profile, **validated_data)

class Property