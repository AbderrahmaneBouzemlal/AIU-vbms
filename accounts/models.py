from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('advisor', 'Advisor'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    )
    username = None
    email = models.EmailField(unique=True)
    student_id = models.CharField(unique=True, max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    USERNAME_FIELD = student_id
    REQUIRED_FIELDS = [user_type, email, student_id, phone_number]
    class Meta:
        db_table = 'user'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    staff_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'user_profile'