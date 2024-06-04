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
from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist

@api_view(['POST'])
def add_book(request):
    name = request.data.get('name')
    author = request.data.get('author')
    publisher_id = request.data.get('publisher_id')
    stock = request.data.get('stock')
    price = request.data.get('price')
    book = Book.objects.create(name=name, author=author, publisher_id=publisher_id, stock=stock, price=price)
    book.save()
    return Response({'status': 'Book added successfully'}, status=201)

@api_view(['GET', 'POST'])
def books(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Book added successfully'}, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PUT', 'DELETE'])
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=404)

    if request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Book updated successfully'}, status=200)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        book.delete()
        return Response({'status': 'Book deleted successfully'}, status=204)
    

    
@api_view(['GET'])
def get_pending_users(request):
    pending_users = Customuser.objects.filter(is_active=False, user_type=1)
    serializer = UserSerializer(pending_users, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def approve_user(request, user_id):
    try:
        user = Customuser.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return Response({'message': 'User approved successfully'})
    except Customuser.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    # password = request.data.get('password')
    user_type = request.data.get('user_type')
    # Create User object and save to database
    password = ''.join(random.choices(string.digits, k=6))
    user = Customuser.objects.create(username=username, email=email,user_type=user_type)
    user.set_password(password)
    user.save()
    
    
    subject='Regsitration Success'
    message='username:'+str(username)+"\n"+'password:'+str(password)+"\n"+'email:'+str(email)
    send_mail(subject,message,settings.EMAIL_HOST_USER,{user.email})
    messages.info(request,'Registration success, please check your email for username and password..')
    return Response({'message': 'User registered successfully'})


@api_view(['GET'])
def get_books(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_rentals(request):
    rentals = Rental.objects.all()
    serializer = RentalSerializer(rentals, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def rent_book(request):
    book_id = request.data.get('book')
    try:
        book = Book.objects.get(id=book_id)
        if book.stock > 0:
            rental = Rental.objects.create(book=book, due_date=request.data.get('due_date'))
            book.stock -= 1
            book.save()
            serializer = RentalSerializer(rental)
            return Response(serializer.data, status=201)
        else:
            return Response({'message': 'Book out of stock'}, status=400)
    except ObjectDoesNotExist:
        return Response({'message': 'Book not found'}, status=404)

@api_view(['POST'])
def report_lost_book(request):
    rental_id = request.data.get('rental_id')
    try:
        rental = Rental.objects.get(id=rental_id)
        if not rental.returned and not rental.lost:
            rental.lost = True
            # Calculate fine amount (example: original price + additional charges)
            rental.fine_amount = rental.book.price + 10  # Dummy calculation
            rental.save()
            return Response({'message': 'Book reported as lost'}, status=200)
        else:
            return Response({'message': 'Invalid operation'}, status=400)
    except ObjectDoesNotExist:
        return Response({'message': 'Rental not found'}, status=404)

class UserViewSet(viewsets.ModelViewSet):
    queryset = Customuser.objects.all()
    serializer_class = UserSerializer

    # @action(detail=False, methods=['post'])
    # def approve_user(self, request):
    #     user_id = request.data.get('user_id')
    #     try:
    #         user = Customuser.objects.get(id=user_id)
    #         user.is_approved = True
    #         user.save()
    #         return Response({'status': 'User approved'}, status=status.HTTP_200_OK)
    #     except Customuser.DoesNotExist:
    #         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
            fine_amount = rental.book.price + 10  
            return Response({'fine': fine_amount}, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({'error': 'Rental not found'}, status=status.HTTP_404_NOT_FOUND)

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


                


