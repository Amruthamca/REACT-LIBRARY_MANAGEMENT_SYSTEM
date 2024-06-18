from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime,date


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
    fine_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def calculate_fine(self):
        if not self.returned:
            today=date.today()
            overdue_days = (today - self.due_date).days
            if overdue_days > 0:
                self.fine_amount = self.book.price + (overdue_days * 1)  
                self.save()

class Purchase(models.Model):
    user = models.ForeignKey(Customuser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    book_name=models.CharField(max_length=200,null=True)

    


