from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView,UserViewSet,RentalViewSet
from .import views
from .views import RentBookView, ReportLostBookView, RentalHistoryView

router = DefaultRouter()
router.register(r'users',UserViewSet)
router.register(r'rentals', RentalViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login',LoginView.as_view(),name='login'),
    path('users/',views.register_user,name='users'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('add_book/', views.add_book, name='add_book'),
    path('books/', views.books, name='books'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('pending-users/', views.get_pending_users, name='get_pending_users'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('books/', views.get_books, name='get_books'),
     path('rentals/rent/',views. rent_book, name='rent_book'),
    
    path('reset-password/', views.reset_password, name='reset_password'),
    path('pending-users/', views.pending_users, name='pending_users'),
    path('approve-user/', views.approve_user, name='approve_user'),

    path('purchases', views.create_purchase, name='create_purchase'),
    path('view_purchase/',views.view_purchase,name='view_purchase'),
    
    

    path('rent-book/<int:book_id>', RentBookView.as_view(), name='rent-book'),
    # path('rentals/report-lost/<int:rental_id>/', ReportLostBookView.as_view(), name='report-lost'),
    # path('rentals/history/', RentalHistoryView.as_view(), name='rental-history'),

    path('rental_history', views.rental_history, name='rental_history'),
    path('report-lost/<int:id>', views.report_lost, name='report_lost'),
    path('return-book/<int:rental_id>', views.return_book, name='return-book'),

    path('user_rentals/', views.user_rentals, name='user_rentals'),
    path('view_purchase_history/', views.view_purchase_history, name='view_purchase_history'),

    
    
    

    
]