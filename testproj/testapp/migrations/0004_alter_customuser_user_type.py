# Generated by Django 5.0.5 on 2024-06-03 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0003_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.IntegerField(default=0),
        ),
    ]
