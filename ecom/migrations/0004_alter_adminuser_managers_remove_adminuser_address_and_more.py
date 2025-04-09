# Generated by Django 5.1.7 on 2025-04-06 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0003_adminuser_address_adminuser_mobile_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='adminuser',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='address',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='adminuser',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='username',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='customer',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='customer_profile/'),
        ),
    ]
