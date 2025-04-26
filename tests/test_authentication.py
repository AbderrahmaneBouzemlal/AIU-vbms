import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from accounts.models import StudentProfile, StaffProfile, AdminProfile
from accounts.serializers import StaffProfileSerializer, AdminProfileSerializer, StudentProfileSerializer, \
    UserSerializer


@pytest.fixture
def api_client():
    return APIClient()


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
@pytest.mark.django_db
class TestRegisterView:
    url = reverse('register')

    def test_user_registration_success(self, api_client):
        data = {
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'user_type': 'STUDENT'
        }

        response = api_client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'user_id' in response.data
        assert response.data['status'] == 'success'
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_user_registration_invalid_data(self, api_client):
        data = {
            'email': 'invalid-email',
            'password': 'weak',
            'user_type': 'INVALID'
        }

        response = api_client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
        assert 'errors' in response.data

@pytest.mark.django_db
class TestLoginView:
    url = reverse('login')

    def test_login_success(self, api_client, create_user):
        user = create_user()
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(self.url, data)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'refresh' in response.data['tokens']
        assert 'user_id' in response.data
        assert response.data['user_type'] == 'student'

    def test_login_invalid_credentials(self, api_client, create_user):
        user = create_user()
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post(self.url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'errors' in response.data
        assert response.data['status'] == 'error'

@pytest.mark.django_db
class TestUserProfileView:
    url = reverse('profile')

    def test_get_profile_authenticated(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['profile'] is not None

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestUnifiedProfileView:
    url = reverse('profile')

    def test_get_student_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            profile_data={'major': 'Biology', 'year': 2}
        )
        api_client.force_authenticate(user=student)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == student.email
        print(response.data)
        assert response.data['profile']['major'] == 'Biology'
        assert response.data['profile']['year'] == 2

    def test_get_staff_profile(self, api_client, create_user):
        staff = create_user(
            email="staff@example.com",
            user_type="staff",
            profile_data={'department': 'SA'}
        )
        api_client.force_authenticate(user=staff)

        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'staff@example.com'
        assert response.data['profile']['department'] == 'SA'

    def test_update_student_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            first_name="Original",
            last_name="Student",
            profile_data={'major': 'Math', 'year': 1}
        )
        api_client.force_authenticate(user=student)

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Student',
            'profile': {
                'major': 'Computer Science',
                'year': 3
            }
        }

        response = api_client.put(self.url, update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Student'
        assert response.data['profile']['major'] == 'Computer Science'
        assert response.data['profile']['year'] == 3

        student.refresh_from_db()
        assert student.first_name == 'Updated'
        assert student.last_name == 'Student'
        assert student.studentprofile.major == 'Computer Science'
        assert student.studentprofile.year == 3

    def test_update_staff_profile(self, api_client, create_user):
        staff = create_user(
            email="staff@example.com",
            user_type="staff",
            first_name="Original",
            last_name="Staff",
            profile_data={'department': 'PPK'}
        )
        api_client.force_authenticate(user=staff)

        update_data = {
            'first_name': 'Updated',
            'last_name': 'Staff',
            'profile': {
                'department': 'SA'
            }
        }

        response = api_client.put(self.url, update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Staff'
        assert response.data['profile']['department'] == 'SA'

        staff.refresh_from_db()
        assert staff.first_name == 'Updated'
        assert staff.last_name == 'Staff'
        assert staff.staffprofile.department == 'SA'

    def test_update_profile_unauthorized(self, api_client, create_user):
        update_data = {
            'first_name': 'wrong',
            'last_name': 'name',
            'profile': {'major': 'Fail'}
        }
        response = api_client.put(self.url, update_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_partial_update_profile(self, api_client, create_user):
        student = create_user(
            user_type="student",
            profile_data={'major': 'Physics', 'year': 2}
        )
        api_client.force_authenticate(user=student)

        update_data = {
            'profile': {
                'major': 'Chemistry'
            }
        }

        response = api_client.patch(self.url, update_data, format='json')

        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['profile']['major'] == 'Chemistry'
        assert response.data['profile']['year'] == 2