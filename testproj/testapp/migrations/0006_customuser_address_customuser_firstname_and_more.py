# Generated by Django 5.0.5 on 2024-06-25 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0005_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='address',
            field=models.CharField(default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='customuser',
            name='firstname',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='customuser',
            name='lastname',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='customuser',
            name='mobileno',
            field=models.CharField(default='', max_length=15),
        ),
    ]
