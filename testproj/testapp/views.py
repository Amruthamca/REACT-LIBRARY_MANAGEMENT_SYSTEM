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
from django.views.decorators.http import require_GET, require_POST
import json
from django.shortcuts import redirect
import random
from rest_framework.decorators import api_view,permission_classes
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from django.contrib import messages
from django.shortcuts import get_object_or_404
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

@require_GET
def get_books(request):
    books = Book.objects.all()
    books_list = [{"id": book.id, "name": book.name, "author": book.author, "stock": book.stock} for book in books]
    return JsonResponse(books_list, safe=False)

@require_POST
def rent_book(request):
    try:
        data = json.loads(request.body)
        book_id = data['book']
        due_date = data['due_date']
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=403)

        book = get_object_or_404(Book, id=book_id)
        
        if book.stock <= 0:
            return JsonResponse({'error': 'Book out of stock'}, status=400)

        rental = Rental.objects.create(book=book, user=user, due_date=due_date)
        book.stock -= 1
        book.save()
        
        return JsonResponse({'message': 'Book rented successfully', 'due_date': due_date}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
def purchase_books(request):
    try:
        data = json.loads(request.body)
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=403)

        purchases = []
        for item in data:
            book_id = item['book']
            quantity = item['quantity']
            book = get_object_or_404(Book, id=book_id)
            
            if book.stock < quantity:
                return JsonResponse({'error': f'Not enough stock for book: {book.name}'}, status=400)
            
            purchase = Purchase.objects.create(book=book, user=user, quantity=quantity)
            book.stock -= quantity
            book.save()
            purchases.append({'book': book.name, 'quantity': quantity})
        
        # Send confirmation email
        subject = 'Purchase Confirmation'
        message = f'Your purchase has been successful. Details: {purchases}'
        from_email = 'amruthabiju1227@gmail.com'  # Update with your email
        to_email = [user.email]  # Assuming user has an email field

        send_mail(subject, message, from_email, to_email)

        return JsonResponse({'message': 'Purchase successful', 'purchases': purchases}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
def reset_password(request):
    username = request.data.get('username')
    old_password = request.data.get('Current_password')
    new_password = request.data.get('New_password')

    user = authenticate(username=username, password=old_password)
    if user is not None:
        if len(new_password) < 6 or not any(char.isupper() for char in new_password) \
                     or not any(char.isdigit() for char in new_password) \
                     or not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/~' for char in new_password):
            return JsonResponse({'message': 'Password must be at least 6 characters long and contain at least one uppercase letter, one digit, and one special character, or entered password does not match'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
# def logout_view(request):
#     request.session.clear()  
#     return redirect('/') 

class UserViewSet(viewsets.ModelViewSet):
    queryset = Customuser.objects.all()
    serializer_class = UserSerializer


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


                


