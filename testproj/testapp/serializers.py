# users/serializers.py

from .models import Customuser, Book, Rental, Purchase
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customuser
        fields = ('id', 'username', 'email', 'is_approved')

    def create(self, validated_data):
        user = Customuser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            
            # password=str(random.randint(100000,999999))
            
        )
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


   

