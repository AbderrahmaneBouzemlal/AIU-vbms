from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from PIL import Image


class User(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    )
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    phone_number = models.CharField(max_length=20)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [user_type]
    objects = UserManager()


    class Meta:
        db_table = 'auth_user'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', default="profile_pics/default_profilepic.jpg",)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=(('male', 'Male'), ('female', 'Female')))
    location = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'user_profile'


    def save(self, *args, **kwargs):
        super().save()
        if self.profile_picture is None:
            self.profile_picture = "profile_pics/default_profilepic.jpg"


def upload_to(instance, filename):
    return f'images/{filename}'


class StudentProfile(UserProfile):
    student_id = models.CharField(max_length=20, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(default=1)

    class Meta:
        db_table = 'student_profile'



class StaffProfile(UserProfile):
    staff_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True,
                                 choices=(('PPK', 'PPK'), ('SA', 'SA')))

    class Meta:
        db_table = 'staff_profile'


class AdminProfile(UserProfile):
    admin_id = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'admin_profile'
