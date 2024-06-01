# signals.py

from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def set_user_type(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            instance.user_type = CustomUser.SUPERUSER
        else:
            instance.user_type = CustomUser.REGULAR_USER
        instance.save()
