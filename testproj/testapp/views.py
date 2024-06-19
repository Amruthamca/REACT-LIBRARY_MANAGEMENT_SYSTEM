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
from django.contrib.auth import get_user_model
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
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta,date
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
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

# @require_POST
# def rent_book(request):
#     try:
#         data = json.loads(request.body)
#         book_id = data['book']
#         due_date = data['due_date']
#         user = request.user

#         if not user.is_authenticated:
#             return JsonResponse({'error': 'User not authenticated'}, status=403)

#         book = get_object_or_404(Book, id=book_id)
        
#         if book.stock <= 0:
#             return JsonResponse({'error': 'Book out of stock'}, status=400)

#         rental = Rental.objects.create(book=book, user=user, due_date=due_date)
#         book.stock -= 1
#         book.save()
        
#         return JsonResponse({'message': 'Book rented successfully', 'due_date': due_date}, status=201)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)




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
    queryset = Customuser.objects.filter(is_approved=0)
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        user.save()

        
        send_mail(
            'Account Approved',
            'Your account has been approved.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({'status': 'user approved'})

    @action(detail=True, methods=['post'])
    def disapprove(self, request, pk=None):
        user = self.get_object()
        user.delete()

        
        send_mail(
            'Account Disapproved',
            'Your account has been disapproved.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({'status': 'user disapproved'})


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
                return JsonResponse({'access':str(refresh.access_token),'role':role, 'user':user.id },safe=False)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# class RentalViewSet(viewsets.ModelViewSet):
#     queryset = Rental.objects.all()
#     serializer_class = RentalSerializer

#     @action(detail=False, methods=['post'])
#     def report_lost(self, request):
#         rental_id = request.data.get('rental_id')
#         try:
#             rental = Rental.objects.get(id=rental_id)
#             rental.lost = True
#             rental.save()
#             fine_amount = rental.book.price + 10  
#             return Response({'fine': fine_amount}, status=status.HTTP_200_OK)
#         except Rental.DoesNotExist:
#             return Response({'error': 'Rental not found'}, status=status.HTTP_404_NOT_FOUND)

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


# function to handle renting a book
def rent_book(request):
    if request.method == 'POST':
        book_id = request.data.get('book_id')
        due_date = timezone.now() + timezone.timedelta(days=14)  # 14-day rental period
        # Your logic to create a rental record goes here
        return Response({'due_date': due_date}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid request method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

User = get_user_model()

def pending_users(request):
    if request.method == 'GET':
        users = User.objects.filter(is_approved=False, user_type=1)
        users_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
        return JsonResponse(users_data, safe=False)

User = get_user_model()

@api_view(['POST'])
def pending_users(request):
    # if request.method == 'GET':
        users = Customuser.objects.filter(is_approved=0)
        print("hai")
        print(users)
        users_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
        a=1
        return JsonResponse({'users_data':users_data,'a':a})
    # else:
    #     return Response({"message":"Invalid"})

@csrf_exempt  # Ensure to secure this endpoint in production
def approve_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('userId')
        is_approved = data.get('isApproved')
        user = get_object_or_404(User, id=user_id)
        user.is_approved = is_approved
        user.save()

        # Sending email to the user
        subject = 'Account Approval Status'
        message = f'Your account has been {"approved" if is_approved else "disapproved"} by the admin.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, email_from, recipient_list)
        
        return JsonResponse({"message": "User status updated successfully"})
    
# class RentBookView(APIView):
#     def post(self, request, book_id, *args, **kwargs):
#         try:
#             book = Book.objects.get(id=book_id)
#             rental_period = request.data.get('rentalPeriod', 1)
#             if book.stock > 0:
#                 book.stock -= 1 
#                 book.save()
#                 due_date = datetime.now() + timedelta(days=int(rental_period))
                
#                 return Response({"message": "Book rented successfully", "due_date": due_date.strftime('%Y-%m-%d')}, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": "Book out of stock"}, status=status.HTTP_400_BAD_REQUEST)
#         except Book.DoesNotExist:
#             return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        
# class ReportLostBookView(APIView):
#     def post(self, request, rental_id, *args, **kwargs):
#         try:
#             rental = Rental.objects.get(id=rental_id)
#             rental.lost = True
#             rental.calculate_fine()
#             rental.save()
#             return Response({"message": "Book reported as lost", "fine_amount": rental.fine_amount}, status=status.HTTP_200_OK)
#         except Rental.DoesNotExist:
#             return Response({"error": "Rental not found"}, status=status.HTTP_404_NOT_FOUND)

# class RentalHistoryView(APIView):
#     def get(self, request, *args, **kwargs):
#         rentals = Rental.objects.filter(user=request.user)
#         serializer = RentalSerializer(rentals, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)



class RentBookView(APIView):
    def post(self, request, book_id, *args, **kwargs):
        try:
            book = Book.objects.get(id=book_id)
            rental_period = request.data.get('rentalPeriod', 1)
            user = request.user
            
            if book.stock > 0:
                book.stock -= 1
                book.save()
                
                due_date = date.today() + timedelta(days=int(rental_period))
                
                rental = Rental.objects.create(
                    user=user,
                    book=book,
                    due_date=due_date,
                )
                
                serializer = RentalSerializer(rental)
                
                return Response({
                    "message": "Book rented successfully",
                    "due_date": due_date, 
                    "rental": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Book out of stock"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @require_GET
# def view_rentals(request):
#      rentals = Rental.objects.all()
#      data = list(rentals.values('id','book','rental_date','due_date','book_name','author_name'))
#      return JsonResponse(data,safe=False)

class RentalHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        rentals = Rental.objects.filter(user=request.user)
        serializer = RentalSerializer(rentals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportLostBookView(APIView):
    def post(self, request, rental_id, *args, **kwargs):
        try:
            rental = Rental.objects.get(id=rental_id, user=request.user)
            rental.lost = True
            rental.calculate_fine()
            rental.save()
            return Response({"message": "Book reported as lost", "fine_amount": rental.fine_amount}, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({"error": "Rental not found"}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(['GET'])
@require_GET
@permission_classes([IsAuthenticated])
def rental_history(request):
    user = request.user
    print(user)
    rentals = Rental.objects.filter(user=user)
    data = [
        {
            'id': rental.id,
            'book_name': rental.book.name,
            'author': rental.book.author,
            'rental_date': rental.rental_date,
            'due_date': rental.due_date,
            'returned': rental.returned,
            'lost': rental.lost
        } for rental in rentals
    ]
    return JsonResponse(data,safe=False)

@api_view(['POST'])
def report_lost(request, id):
    try:
        rental = Rental.objects.get(id=id)
        rental.lost = True
        rental.calculate_fine()  
        rental.save()
        return Response({'fine_amount': rental.fine_amount}, status=status.HTTP_200_OK)
    except Rental.DoesNotExist:
        return Response({'error': 'Rental not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def return_book(request, rental_id):
    try:
        rental = Rental.objects.get(id=rental_id)

        if rental.returned:
            return Response({'message': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

        
        rental.returned = True
        rental.save()

        book = rental.book
        book.stock += 1
        book.save()

        return Response({'message': 'Book returned successfully!'}, status=status.HTTP_200_OK)
    except Rental.DoesNotExist:
        return Response({'error': 'Rental record not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


@api_view(['POST'])
def create_purchase(request):
    
        user = request.data.get('user')
        book = request.data.get('book')
        purchase_date = request.data.get('purchase_date')
        quantity = request.data.get('quantity')
        total_price = request.data.get('total_price')

        user = request.user
        book = Book.objects.get(id=book)
        book_name=book.name

        purchase = Purchase.objects.create(
            user=user,
            book=book,
            
            purchase_date=purchase_date,
            quantity=quantity,
            total_price=total_price,
            book_name=book_name
        )

        purchase.save()

        send_mail(
            'Purchase Confirmation',
            f'Thank you for your purchase, {user.username}! You bought {purchase.quantity} copies of {book.name}.',
            'amruthabiju1227@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return Response({'message': 'Purchase successfully completed'}, status=status.HTTP_201_CREATED)


@require_GET
def view_purchase(request):
     purchase = Purchase.objects.all()
     data = list(purchase.values('id','book','purchase_date','quantity','total_price','book_name'))
     return JsonResponse(data,safe=False)

@require_GET
def user_rentals(request):
    rentals = Rental.objects.select_related('user', 'book').all()
    rental_data = [{
        'username': rental.user.username,
        'email': rental.user.email,
        'book_name': rental.book.name,
        'author_name': rental.book.author,
        'rental_date': rental.rental_date,
        'due_date': rental.due_date,
        'returned': rental.returned,
        'lost': rental.lost,
        'number_of_days': (rental.due_date - rental.rental_date).days,
    } for rental in rentals]
    return JsonResponse({'rentals': rental_data})

@require_GET
def view_purchase_history(request):
    filters = request.GET
    purchases = Purchase.objects.select_related('user', 'book').all()
    

    if 'username' in filters:
        purchases = purchases.filter(user__username=filters['username'])
    if 'email' in filters:
        purchases = purchases.filter(user__email=filters['email'])
    if 'book_name' in filters:
        purchases = purchases.filter(book__name=filters['book_name'])
    if 'author' in filters:
        purchases = purchases.filter(book__author=filters['author'])

    purchase_data = [
        {
            'id': purchase.id,
            'username': purchase.user.username,
            'email': purchase.user.email,
            'book_name': purchase.book.name,
            'author': purchase.book.author,
            'purchase_date': purchase.purchase_date,
            'quantity': purchase.quantity,
            'total_price': purchase.total_price,
        }
        for purchase in purchases
    ]
    return JsonResponse(purchase_data, safe=False)
    

            