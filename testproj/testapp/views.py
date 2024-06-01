# users/views.py
from rest_framework import viewsets
from .models import Customuser, Book, Rental, Purchase
from rest_framework import generics,status
from .serializers import UserSerializer,LoginSerializer, BookSerializer, RentalSerializer, PurchaseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
import string
import random
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action


class UserViewSet(viewsets.ModelViewSet):
    queryset = Customuser.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def approve_user(self, request):
        user_id = request.data.get('user_id')
        try:
            user = Customuser.objects.get(id=user_id)
            user.is_approved = True
            user.save()
            return Response({'status': 'User approved'}, status=status.HTTP_200_OK)
        except Customuser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def perform_create(self, serializer):
        user = serializer.save()
        random_password = ''.join(random.choices(string.digits, k=6))
        user.set_password(random_password)
        user.save()
        send_mail(
            'Welcome !',
            'Thank you for registering.Your temporary password is: '+random_password,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        send_mail(
            'New User Registration',
            f'New user {user.username} has registered and is pending approval.',
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            password = request.data.get('password')
            user = authenticate(username = email, password = password)
            print('hai')
            print(user)
            if user:
                user_type=user.user_type
                if user_type == 0:
                    role = 'Admin'
                else:
                    role = 'User'

                refresh = RefreshToken.for_user(user)
                
                print(refresh.access_token)
                return JsonResponse({'access':str(refresh.access_token),'role':role},safe=False)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer

    @action(detail=False, methods=['post'])
    def report_lost(self, request):
        rental_id = request.data.get('rental_id')
        try:
            rental = Rental.objects.get(id=rental_id)
            rental.lost = True
            rental.save()
            # Calculate fine
            fine_amount = rental.book.price + 10  # Assuming 10 is the additional charge
            return Response({'fine': fine_amount}, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({'error': 'Rental not found'}, status=status.HTTP_404_NOT_FOUND)

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
                


