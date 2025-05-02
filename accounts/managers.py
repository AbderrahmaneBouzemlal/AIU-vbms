from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user_type = extra_fields.get('user_type')
        if not user_type:
            raise ValueError('User Type is Required')
        if user_type.lower() not in ['student', 'staff', 'admin']:
            raise ValueError('Invalid user type')
        if user_type.lower() == 'staff':
            is_staff = extra_fields.update({'is_staff': True})
        if user_type.lower() == 'admin':
            is_staff = extra_fields.update({
                'is_staff': True,
                'is_superuser': True
            })
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)
