from django.db import models
from django.contrib.auth.models import AbstractUser


class Customuser(AbstractUser):
    user_type=models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)

class Book(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher_id = models.CharField(max_length=255)
    stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Rental(models.Model):
    user = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)
    lost = models.BooleanField(default=False)

class Purchase(models.Model):
    user = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    


