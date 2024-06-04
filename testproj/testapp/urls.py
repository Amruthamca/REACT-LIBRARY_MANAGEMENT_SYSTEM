from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView
from .import views

router = DefaultRouter()



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
    path('books/', views.get_books,name='get_books'),
    path('rentals/', views.get_rentals,name='get_rentals'),
    path('rentals/rent_book/', views.rent_book,name='rent_book'),
    path('rentals/report_lost_book/', views.report_lost_book,name='report_lost_book'),
    
    # path('pending-approvals/', views.pending_approvals, name='pending-approvals'),
    # path('approve-user/', views.approve_user, name='approve-user'),
    # path('add-book/', views.add_book, name='add_book'),
    # path('manage-books/', views.manage_books, name='manage_books'),
    # path('user-history/', views.user_history, name='user_history'),
    
    

    
]