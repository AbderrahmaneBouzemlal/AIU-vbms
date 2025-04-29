import pytest
from rest_framework.test import APIClient
from accounts.models import User, StudentProfile, StaffProfile, AdminProfile
from accounts.serializers import StaffProfileSerializer, AdminProfileSerializer, StudentProfileSerializer, \
    UserSerializer


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def registered_user_data():
    return {
        'first_name': 'Abderrahmane',
        'last_name': 'BouBou',
        'email': 'Abderrahmane@gmail.com',
        'password': 'Passw@#RVord',
        'user_type': 'student',
    }

@pytest.fixture
def create_user(db, django_user_model):
    def _create_user(email="test@example.com", password="testpass123",
                     user_type="student", profile_data=None, **kwargs):
        user = django_user_model.objects.create_user(
            email=email,
            password=password,
            user_type=user_type,
            **kwargs
        )
        if profile_data:
            if user.user_type == 'admin':
                profile = AdminProfile.objects.get(user=user)
                serializer = AdminProfileSerializer(profile, data=profile_data, partial=True)
            elif user.user_type == 'staff':
                profile = StaffProfile.objects.get(user=user)
                serializer = StaffProfileSerializer(profile, data=profile_data, partial=True)
            else:
                profile = StudentProfile.objects.get(user=user)
                serializer = StudentProfileSerializer(profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return user

    return _create_user