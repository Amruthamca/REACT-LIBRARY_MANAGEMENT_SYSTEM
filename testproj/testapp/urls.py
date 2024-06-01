from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet,LoginView, BookViewSet, RentalViewSet, PurchaseViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
router.register(r'rentals', RentalViewSet)
router.register(r'purchases', PurchaseViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login',LoginView.as_view(),name='login'),
    

    
]