from .models import Customuser, Book, Rental, Purchase
from rest_framework import serializers
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customuser
        fields = ('id', 'username', 'email', 'user_type')

    

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


   
